from datetime import datetime

import importlib
import pytz
from django.db import connection, transaction, models
from restless.exceptions import NotFound
from sana_pchr.api import CredentialsResource

#Need these imports! Uses system imports for name lookup
from sana_pchr.models.medication import *
from sana_pchr.models import *
import sys

import pdb

class SynchronizationProcessor:
    class SynchronizationException(Exception):
        pass

    def __init__(self, device, model):
        self.device = device
        self._models = model
        # Sharded models are the ones that should not be totally synchronized with the device
        self._sharded_models = [x.__name__ for x in list([Medication, Patient, Visit, Encounter, Record, Test, Physician,
                                                          Device, Clinic_Physician, Clinic, Patient_Physician, Event ])]
        self._not_sharded_models = list(set(self._models) - set(self._sharded_models))

    def _take_sync_lock(self):
        if connection.vendor == 'mysql':
            connection.cursor().execute("SELECT GET_LOCK('sync', 9999999)")
            # TODO implement elif connection.vendor == 'postgresql':

    def _release_sync_lock(self):
        if connection.vendor == 'mysql':
            connection.cursor().execute("SELECT RELEASE_LOCK('sync')")
            # TODO implement elif connection.vendor == 'postgresql':

    def update_patient(self, patients, since=False):
        self._take_sync_lock()
        try:
            if type(patients) == Patient:
                patients = [patients]

            visits = Visit.objects.filter(patient__in=patients)
            encounters = Encounter.objects.filter(visit__in=visits).select_related('physician', 'device', 'clinic')
            tests = Test.objects.filter(encounter__in=encounters)
            records = Record.objects.filter(encounter__in=encounters)
            medications = Medication.objects.filter(encounter__in=encounters)

            # Get related fields from encounters
            physicians = Physician.objects.filter(uuid__in=encounters.values('physician').distinct())
            devices = Device.objects.filter(uuid__in=encounters.values('device').distinct())
            clinics = Clinic.objects.filter(uuid__in=encounters.values('clinic').distinct())

            returnList = ((Physician, physicians), (Patient, patients), (Clinic, clinics),
                          (Device, devices), (Visit, visits), (Encounter, encounters),
                          (Test, tests), (Record, records),  (Medication, medications))

            # Check if any have been updated since
            if since:
                returnList = ((x, y.filter(synchronized__gt=since)) for (x, y) in returnList)

            returnList = ((x, y) for (x, y) in returnList if y)

            yield from returnList
        finally:
            self._release_sync_lock()

    def add_patient(self, patient_id, physician_id):
        try:
            the_patient = Patient.objects.get(uuid=patient_id)
            Patient_Physician(patient=the_patient,
                              physician=Physician.objects.get(uuid=physician_id)).save()

            yield from self.update_patient(the_patient)
        except models.ObjectDoesNotExist:
            raise NotFound()

    def add_physician(self, physician_id):
        if physician_id:
            # Need to sync
            try:
                the_physician = Physician.objects.get(uuid=physician_id)
                Clinic_Physician(clinic=self.device.clinic, physician=the_physician).save()
                yield the_physician
            except models.ObjectDoesNotExist:
                raise NotFound()
        else:
            raise NotFound()

    def search_physician_contact(self, contact_info):
        if contact_info:
            try:

                # is it email or phone?
                if '@' in contact_info:
                    the_physician = Physician.objects.get(email=contact_info)
                else:
                    the_physician = Physician.objects.get(phone=contact_info)
                Clinic_Physician(clinic=self.device.clinic, physician=the_physician).save()
                yield the_physician
            except models.ObjectDoesNotExist:
                raise NotFound()
        else:
            raise NotFound()

    def search_patient_unhcr(self, unhcr_id):
        if unhcr_id:
            patients = Patient.objects.filter(UNHCR=unhcr_id)
            if patients.exists():
                yield (Patient, patients)
            else:
                raise NotFound()
        else:
            raise NotFound()

    def search_patient(self, year, first, last, city, gender):
        if year:
            patients = Patient.objects.filter(birthYear__exact=year)
            if city:
                patients = patients.filter(birthCity__istartswith=city)
            if first:
                patients = patients.filter(firstName__istartswith=first)
            if last:
                patients = patients.filter(lastName__istartswith=last)
            if gender:
                patients = patients.filter(gender__exact=gender)
            if patients.exists():
                yield (Patient, patients)
            else:
                raise NotFound()
        else:
            raise NotFound()

    def calculate_delta(self, since):
        # There was a race condition here if someone requests records "since" the current time, while some other worker is inserting new records timestamped at the current time but not yet visible to queries (e.g. transaction hasn't closed)
        # So, wrap the entire thing in a global mutex to prevent concurrent updates
        self._take_sync_lock()

        try:

            for model_name in self._not_sharded_models:
                model = self._model_type(model_name)
                delta_instances = list(model.objects.filter(synchronized__gt=since))
                if delta_instances:
                    yield model, delta_instances

            # If a device's clinic field has recently been updated, download it all.
            if self.device.synchronized > since:
                new_phys = Physician.objects.filter(clinic_physician__clinic=self.device.clinic)
                new_patients = Patient.objects.filter(patient_physician__physician__in=new_phys)
                yield from self.update_patient(new_patients)
            else:
                clinic_physician = Clinic_Physician.objects.filter(clinic=self.device.clinic)
                physicians = Physician.objects.filter(uuid__in=clinic_physician.values('physician'))
                if physicians:
                    patient_physician = Patient_Physician.objects.filter(physician__in=physicians)
                    patients = Patient.objects.filter(uuid__in=patient_physician.values('patient'))
                    if since:
                        patient_physician = patient_physician.filter(synchronized__gt=since)
                        clinic_physician = clinic_physician.filter(synchronized__gt=since)
                    if clinic_physician:
                        yield Clinic_Physician, clinic_physician
                        new_phys = [x.physician for x in clinic_physician]
                        new_patients = Patient.objects.filter(patient_physician__physician__in=new_phys)
                        yield from self.update_patient(new_patients)
                    if patient_physician:
                        yield Patient_Physician, patient_physician
                        new_patients = [x.patient for x in patient_physician]
                        yield from self.update_patient(new_patients)
                    if patients:
                        yield from self.update_patient(patients, since)
        finally:
            self._release_sync_lock()

    # Given a list of modified SynchronizedModels, updates the database per their updated_at and synchronized dates
    # Updates are accomplished by save()ing models given in changed_models.
    def apply_changes(self, changed_models):
        self._take_sync_lock()
        with transaction.atomic():
            try:
                # Lock in a single timestamp for updating synchronized values
                # No real reason other than to make these look nice
                now = datetime.utcnow().replace(tzinfo=pytz.utc)
                mutated_models = []
                for changed_model in changed_models:
                    model = type(changed_model)
                    if model.__name__ in self._models:
                        # We need to exclude FK fields since they are validated live against the database by django
                        # Normally could just wrap everything in a transaction to defer the validation - but it's not the database enforcing the constraints
                        # Instead, we skip validating these relationships until everything's into the transaction
                        fk_fields = [x for x in model._meta.many_to_many + model._meta.fields if hasattr(x.rel, "to")]
                        changed_model.full_clean(
                                exclude=[x.name for x in fk_fields])  # throws when there are validation issues

                        try:
                            reference_model = model.objects.get(uuid=changed_model.uuid)
                        except model.DoesNotExist:
                            # It's a new model, so insert and move on
                            changed_model.save()
                            mutated_models.append(changed_model)
                        else:
                            # Check if we deleted the model on server
                            if changed_model.deleted > reference_model.deleted:
                                pass
                            elif changed_model.synchronized > reference_model.synchronized:
                                # Only we should be updating the synchronized record, nobody else
                                raise SynchronizationProcessor.SynchronizationException(
                                        "Remote record synchronized later than local record - server rollback?")
                            else:
                                if changed_model.updated < reference_model.updated:
                                    # The update being pushed is older than somebody else's that's already integrated
                                    # So, throw out this update
                                    # (a 3-way diff would provide more resilient conflict resolution)
                                    # (but would also require a much more complicated revisioning system, storage of all revision history, etc)
                                    pass
                                else:
                                    # Incoming data is newer than what we have - use the incoming data
                                    changed_model.synchronized = now
                                    changed_model.save()
                                    mutated_models.append(changed_model)
                    else:
                        # If there are models that aren't what they are supposed to be
                        raise SynchronizationProcessor.SynchronizationException(
                                "Model %s provided, not within synchronization scope" % changed_model)
                # It's at this point - when all the changes are "saved" (but still in the transaction) that we verify relationships
                # If any of these validations fail, the transaction is aborted and no changes are applied
                for mutated_model in mutated_models:
                    mutated_model.full_clean()
            finally:
                self._release_sync_lock
            self.device.lastSynchronized = DefaultFuncs.getNow()

    def _model_type(self, model):
        # Wheee
        return getattr(sys.modules[__name__], model)


# This is purely concerned with wrapping the Restless model interfacing
class SerializedSynchronizationProcessor(SynchronizationProcessor):
    def __init__(self, device):
        # Auto-discover restless resources
        # Currently these are used only to define the serialization output
        from sana_pchr.api.base import SynchronizedResource

        def all_subclasses(cls):
            return cls.__subclasses__() + [x for y in cls.__subclasses__() for x in all_subclasses(y)]

        self._resource_mapping = {}
        for synced_resource in SynchronizedResource.__subclasses__():
            self._resource_mapping[synced_resource.model] = synced_resource()

        super(SerializedSynchronizationProcessor, self).__init__(device,
                                                                 [x.__name__ for x in self._resource_mapping.keys()])

    # Uses the corresponding restless model's fieldpreparer for serialization
    def calculate_delta(self, since):

        delta_model_pairs = super(SerializedSynchronizationProcessor, self).calculate_delta(since)
        return self.serialize_return(delta_model_pairs)

    def add_patient(self, patient, the_physician):
        result = super(SerializedSynchronizationProcessor, self).add_patient(patient, the_physician)
        return self.serialize_return(result)

    def add_physician(self, physician_id):
        result = super(SerializedSynchronizationProcessor, self).add_physician(physician_id)
        return CredentialsResource.serialize_physicians(self.device, result)

    def search_physician_contact(self, contact_info):
        result = super(SerializedSynchronizationProcessor, self).search_physician_contact(contact_info)
        return CredentialsResource.serialize_physicians(self.device, result)

    def search_patient_unhcr(self, unhcr_id):
        result = super(SerializedSynchronizationProcessor, self).search_patient_unhcr(unhcr_id)
        return self.serialize_return(result)

    def search_patient(self, year, first, last, city, gender):
        result = super(SerializedSynchronizationProcessor, self).search_patient(year, first, last, city, gender)
        return self.serialize_return(result)

    def serialize_return(self, data):
        result_dict = {}
        for model, delta_instances in data:
            if model not in self._resource_mapping:
                raise Exception("No SynchronizedResource for %s" % model.__name__)
            result_dict[model.__name__] = [self._resource_mapping[model].prepare(x) for x in delta_instances]
        return result_dict

    # We simply paste the updated values into the model without much rehydration - hopefully this is durable enough for the time being
    # In the future, could use the restless model's update() operations or something, which in turn can use ModelForms
    def apply_changes(self, changed_models_dict):
        changed_model_instances = []

        # Order model names in a way that we won't break references
        category_order = [x.__name__ for x in CategoryModel.__subclasses__()]
        sync_order = ["Physician", "Patient", "Clinic", "Device", "Visit", "Encounter", "Test", "Record", "Medication",
                      "Patient_Physician", "Clinic_Physician","Event"]

        for model_name in category_order + sync_order:
            if model_name in changed_models_dict.keys():
                changed_models = changed_models_dict[model_name]
                model = self._model_type(model_name)
                model_resource = self._resource_mapping[model]
                for changed_model in changed_models:
                    # Filter to only valid model fields
                    # (and munge FKs a bit)
                    whitelisted_fields = [(x.db_column if x.db_column else x.name) for x in
                                          model._meta.fields + model._meta.many_to_many]
                    changed_model = {k: v for k, v in changed_model.items() if k in whitelisted_fields}
                    # rehydrate FKs (maybe ditching tastypie was a bad idea after all?)
                    for fk_field in [x for x in model._meta.fields if hasattr(x.rel, "to")]:
                        dbcol = fk_field.db_column if fk_field.db_column else fk_field.name
                        if dbcol in changed_model:
                            # This is a cheap trick to make the FKs resolve
                            # We instantiate - but don't save - a new Model with the correct UUID and feed that in
                            # This is cheaper than performing a lookup, and doesn't break when the referenced model has yet to be created
                            # We never actually save this model - it just pulls out the PK before caching it in the relation - so the actual record (if it exists) remains untouched
                            # And, finally, full_clean - called later - does actually resolve all references, so this doesn't let you create broken FK relations
                            changed_model[fk_field.name + "_id"] = changed_model[dbcol]
                            del changed_model[dbcol]
                    try:
                        instance = model.objects.get(uuid=changed_model["uuid"])
                        if not model_resource.allow_update:
                            continue
                        for blacklisted_key in model_resource.readonly_update_keys + model_resource._readonly_update_keys:
                            if blacklisted_key in changed_model:
                                del changed_model[blacklisted_key]
                    except model.DoesNotExist:
                        instance = model()
                        if not model_resource.allow_create:
                            continue
                    for blacklisted_key in model_resource.readonly_keys + model_resource._readonly_keys:
                        if blacklisted_key in changed_model:
                            del changed_model[blacklisted_key]
                    # Can't .update the __dict__ because FKs have magic

                    for k, v in changed_model.items():
                        if v != "" and v != "null":
                            setattr(instance, k, v)

                    changed_model_instances.append(instance)

        return super(SerializedSynchronizationProcessor, self).apply_changes(changed_model_instances)
