import json
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch

import pytz

from sana_pchr.api.base import SynchronizedFieldsPreparer, SynchronizedResource
from sana_pchr.models import *
from sana_pchr.models.medication import *
from sana_pchr.models.base import SynchronizedModel
from .base import BaseTestCase
from .utils import deterministic_uuids


class SyncResourceTestCase(BaseTestCase):
    def setUp(self):
        super(SyncResourceTestCase, self).setUp()
        self.now = datetime.utcnow().replace(tzinfo=pytz.utc)
        self.uuid_gen = deterministic_uuids()
        with patch('uuid.uuid4', side_effect=self.uuid_gen):
            self.clinic = Clinic.objects.create(name="cinilC")
            self.clinic2 = Clinic.objects.create(name="Clinic2")
            self.device = Device.objects.create(name="deviceecived", clinic=self.clinic)
            self.record_cat = RecordCategory.objects.create(recordType=123)

    def test_no_auth(self):
        resp = self.client.get('/api/v1/sync/')
        resp.verify(401)

    def _delta_resp(self, params=None):
        ''' Make sure that we can synchronize all the things we care about and that only the physician from our device
         is synchronized
        '''

        params = params if params else {}
        with patch('uuid.uuid4', side_effect=self.uuid_gen):
            now = datetime.utcnow().replace(tzinfo=pytz.utc)
            p1 = Patient.objects.create(firstName="Bob")
            p2 = Patient.objects.create(firstName="Rob")
            py1 = Physician.objects.create(firstName='ilise', lastName='bhat', hashedPIN='1234',
                                           synchronized=self.now - timedelta(seconds=60))
            py2 = Physician.objects.create(firstName='elise', lastName='bhat', hashedPIN='1234',
                                           synchronized=self.now - timedelta(seconds=60))
            Clinic_Physician(clinic=self.clinic, physician=py1).save()
            Clinic_Physician(clinic=self.clinic2, physician=py2).save()
            Patient_Physician.objects.create(patient=p1, physician=py1)
            Patient_Physician.objects.create(patient=p2, physician=py2)

            vc1 = VisitCategory.objects.create()
            ec1 = EncounterCategory.objects.create()
            rc1 = RecordCategory.objects.create(recordType=1)
            tc1 = TestCategory.objects.create(resultType=1)
            v1 = Visit.objects.create(category=vc1, patient=p1)
            e1 = Encounter.objects.create(category=ec1, physician=py1, clinic=self.clinic,
                                               device=self.device, visit=v1)
            r1 = Record.objects.create(value="Testing 123", category=rc1, encounter=e1)
            t1 = Test.objects.create(result="47", category=tc1, encounter=e1)

            iu1 = IntervalUnitCategory.objects.create(displayName="day")
            du1 = DoseUnitCategory.objects.create(displayName="pill")
            mg1 = MedicationGroupCategory.objects.create(displayName="statin")
            mc1 = MedicationCategory.objects.create(displayName="Lipitor", otherName="atorvastatin", group=mg1,
                                          dose_default=1, interval_default=2, times_default=3, dose_unit=du1,
                                          interval_unit=iu1)


            m1 = Medication.objects.create(category=mc1, interval=1, dose=2, times=3, dose_unit=du1,
                                                interval_unit=iu1, end_date=date(2016,2,3), encounter=e1)



            params.update({"synchronized_after": (now - timedelta(seconds=10)).isoformat()})
            return self.client.get('/api/v1/sync/', params, HTTP_AUTHORIZATION="Bearer %s" % self.device.token)

    def test_fetch_delta_no_encryption_override(self):
        from sana_pchr import settings_base
        settings_base.DEBUG = True
        try:
            self._delta_resp({"no_transport_encryption": 1}).verify(200)
        finally:
            settings_base.DEBUG = False

    def test_fetch_delta_no_encryption_override_no_debug(self):
        """ Check to make sure the magic flag doesn't work when DEBUG=False """
        self.assertRaises(UnicodeDecodeError, self._delta_resp({"no_transport_encryption": 1}).content.decode, "utf-8")

    def test_fetch_delta_is_encrypted(self):
        # This will bail at some point (either the decryption, decoding, or parsing) if the response wasn't properly encrypted
        resp = self._delta_resp().content
        plaintext_resp = self.device.key.decrypt(resp).decode("utf-8")
        json.loads(plaintext_resp)


    def test_fetch_through_table_change(self):
        from sana_pchr import settings_base
        settings_base.DEBUG = True
        try:
            with patch('uuid.uuid4', side_effect=self.uuid_gen):
                now = datetime.utcnow().replace(tzinfo=pytz.utc)
                p1 = Patient.objects.create(firstName="Bob", synchronized=self.now - timedelta(seconds=60))
                p2 = Patient.objects.create(firstName="Rob", synchronized=self.now - timedelta(seconds=60))
                py1 = Physician.objects.create(firstName='ilise', lastName='bhat', hashedPIN='1234',
                                               synchronized=self.now - timedelta(seconds=60))
                py2 = Physician.objects.create(firstName='elise', lastName='bhat', hashedPIN='1234',
                                               synchronized=self.now - timedelta(seconds=60))
                Clinic_Physician(clinic=self.clinic, physician=py1).save()
                Clinic_Physician(clinic=self.clinic2, physician=py2).save()
                Patient_Physician.objects.create(patient=p1, physician=py1)
                Patient_Physician.objects.create(patient=p2, physician=py2)

                vc1 = VisitCategory.objects.create()
                ec1 = EncounterCategory.objects.create()
                rc1 = RecordCategory.objects.create(recordType=1)
                tc1 = TestCategory.objects.create(resultType=1)
                v1 = Visit.objects.create(category=vc1, patient=p1, synchronized=self.now - timedelta(seconds=60))
                e1 = Encounter.objects.create(category=ec1, physician=py1, clinic=self.clinic,
                                                   device=self.device, visit=v1, synchronized=self.now - timedelta(seconds=60))
                r1 = Record.objects.create(value="Testing 123", category=rc1, encounter=e1, synchronized=self.now - timedelta(seconds=60))
                t1 = Test.objects.create(result="47", category=tc1, encounter=e1, synchronized=self.now - timedelta(seconds=60))

                iu1 = IntervalUnitCategory.objects.create(displayName="day")
                du1 = DoseUnitCategory.objects.create(displayName="pill")
                mg1 = MedicationGroupCategory.objects.create(displayName="statin")
                mc1 = MedicationCategory.objects.create(displayName="Lipitor", otherName="atorvastatin", group=mg1,
                                              dose_default=1, interval_default=2, times_default=3, dose_unit=du1,
                                              interval_unit=iu1, interaction_warning="warning!")


                m1 = Medication.objects.create(category=mc1, interval=1, dose=2, times=3, dose_unit=du1,
                                                    interval_unit=iu1, end_date=date(2016,2,3), encounter=e1, comment="eat with meal",
                                               synchronized=self.now - timedelta(seconds=60))

                params = {"no_transport_encryption": 1, "synchronized_after": "2001-01-01"}#(now - timedelta(seconds=10)).isoformat()}
                resp = self.client.get('/api/v1/sync/', params, HTTP_AUTHORIZATION="Bearer %s" % self.device.token)
                resp.verify(200, raw=False)
        finally:
            settings_base.DEBUG = False

    def _enc(self, obj):
        serialized = json.dumps(obj).encode("utf-8")
        return self.device.key.encrypt(serialized)

    def test_push_data_no_auth(self):
        resp = self.client.post('/api/v1/sync/', self._enc({"whatever": 123}))
        resp.verify(401)

    def test_push_data_bad_token(self):
        resp = self.client.post('/api/v1/sync/', self._enc({"whatever": 123}), HTTP_AUTHORIZATION="Bearer bob")
        resp.verify(401)

    def test_push_data_bad_crypto(self):
        # Mangle the encrypted data a bit
        data = self._enc({"whatever": 123})
        data = b'1' + data[1:]
        resp = self.client.post('/api/v1/sync/', data, HTTP_AUTHORIZATION="Bearer %s" % self.device.token)
        resp.verify(401)

    def test_push_encounter_m2m_field_update(self):
        '''Test to see if we add an encounter whether or not the related fields are automatically incremented'''

        p1 = Patient(firstName="John")
        p1.save()
        vc1 = VisitCategory()
        vc1.save()
        v1 = Visit(patient=p1, category=vc1)
        ec1 = EncounterCategory()
        ec1.save()
        py1 = Physician(firstName='ilise', lastName='bhat', hashedPIN='1234')
        py1.save()
        e1 = Encounter(visit=v1, clinic=self.clinic, device=self.device, physician=py1, category=ec1)

        test_data = {
            "Encounter": [
                {"visit_uuid": str(v1.uuid), "clinic_uuid": str(self.clinic.uuid),
                 "physician_uuid": str(py1.uuid), "device_uuid": str(self.device.uuid),
                 "uuid": str(e1.uuid), "category_uuid": str(ec1.uuid)}
            ],
            "Visit": [
                {"uuid": str(v1.uuid), "patient_uuid": str(p1.uuid), "category_uuid": str(vc1.uuid)}
            ]
        }

        resp = self.client.post('/api/v1/sync/', self._enc(test_data),
                                HTTP_AUTHORIZATION="Bearer %s" % self.device.token)
        resp.verify(201)

        # Make sure these models have actually materialized
        self.assertEqual(Patient_Physician.objects.get().patient, p1)
        self.assertEqual(Patient_Physician.objects.get().physician, py1)
        self.assertEqual(Clinic_Physician.objects.get().clinic, self.clinic)
        self.assertEqual(Clinic_Physician.objects.get().physician, py1)

    def test_push_updated_data(self):
        '''Make sure updated data is overwritten and unupdated is not'''
        p1 = Patient(firstName="John")
        p2 = Patient(firstName="Bob")
        p1.save()
        p2.save()
        test_data = {
            "Patient": [
                {"firstName": "sehr", "uuid": str(p1.uuid), "updated": str(self.now - timedelta(seconds=60)), "synchronized": "", "end_date": ""},
                {"firstName": "Jose", "uuid": str(p2.uuid), "updated": str(self.now + timedelta(seconds=60)), "synchronized": "", "end_date": ""}
            ],
        }

        resp = self.client.post('/api/v1/sync/', self._enc(test_data),
                                HTTP_AUTHORIZATION="Bearer %s" % self.device.token)
        resp.verify(201)

        # Make sure these models have actually materialized
        self.assertEqual(Patient.objects.get(uuid=p1.uuid).firstName, "John")
        self.assertEqual(Patient.objects.get(uuid=p2.uuid).firstName, "Jose")

    def test_push_old_data(self):
        '''Check to see the effect of pushing data with incorrect synchronization time'''
        p1 = Patient(firstName="John", synchronized=self.now - timedelta(seconds=60))
        p1.save()
        test_data = {
            "Patient": [
                {"firstName": "sehr", "uuid": str(p1.uuid), "synchronized": str(self.now + timedelta(seconds=60)),}
            ],
        }

        resp = self.client.post('/api/v1/sync/', self._enc(test_data),
                                HTTP_AUTHORIZATION="Bearer %s" % self.device.token)
        resp.verify(201)

        # Make sure these models have actually materialized
        self.assertEqual(Patient.objects.get(uuid=p1.uuid).firstName, "sehr")

    # If we push deleted data, remember to delete.
    def test_push_deleted_data(self):
        '''Make sure we ignore deleted data'''
        p1 = Patient(firstName="John", deleted=self.now - timedelta(seconds=60))
        p1.save()
        test_data = {
            "Patient": [
                {"firstName": "sehr", "uuid": str(p1.uuid), "deleted": str(self.now + timedelta(seconds=60))}
            ],
        }

        resp = self.client.post('/api/v1/sync/', self._enc(test_data),
                                HTTP_AUTHORIZATION="Bearer %s" % self.device.token)
        resp.verify(201)

        # Make sure these models have actually materialized
        self.assertEqual(Patient.objects.get(uuid=p1.uuid).firstName, "John")

    def test_push_data(self):
        ''' Check to make sure a full stack push of all data works, fk rehydrating, etc.'''

        p1 = Patient(firstName="John")
        p1.save()
        vc1 = VisitCategory()
        vc1.save()
        v1 = Visit(patient=p1, category=vc1)
        ec1 = EncounterCategory()
        ec1.save()
        py1 = Physician(firstName='ilise', lastName='bhat', hashedPIN='1234')
        py1.save()
        e1 = Encounter(visit=v1, clinic=self.clinic, device=self.device, physician=py1, category=ec1)
        r1 = Record(category=self.record_cat)

        test_data = {
            "Encounter": [
                {"visit_uuid": str(v1.uuid), "clinic_uuid": str(self.clinic.uuid),
                 "physician_uuid": str(py1.uuid), "device_uuid": str(self.device.uuid),
                 "uuid": str(e1.uuid), "category_uuid": str(ec1.uuid)}
            ],
            "Visit": [
                {"uuid": str(v1.uuid), "patient_uuid": str(p1.uuid), "category_uuid": str(vc1.uuid)}
            ],
            "Record": [
                {"uuid": str(r1.uuid), "category_uuid": str(self.record_cat.uuid), "encounter_uuid": str(e1.uuid),
                 "value": "Testing 123"}
            ],
            "Event": [
                { 
                    "device": str(self.device.uuid),
                    "clinic": str(self.clinic.uuid),
                    "user": str(py1.uuid),
                    "status": "SUCCESS",
                    "code": "SYNC_START",
                    "message": "",
                    "exception": ""
                }
            ]
                
        }

        resp = self.client.post('/api/v1/sync/', self._enc(test_data),
                                HTTP_AUTHORIZATION="Bearer %s" % self.device.token)
        resp.verify(201)

        # Make sure these models have actually materialized
        self.assertEqual(Encounter.objects.get(uuid=e1.uuid).physician.uuid, py1.uuid)
        self.assertEqual(Record.objects.get(uuid=r1.uuid).value, "Testing 123")
        self.assertEqual(Record.objects.get(uuid=r1.uuid).encounter.uuid, e1.uuid)
        self.assertEqual(Visit.objects.get(uuid=v1.uuid).patient.uuid, p1.uuid)
        self.assertEqual(Encounter.objects.count(), 1)
        self.assertEqual(Record.objects.count(), 1)
        self.assertEqual(Visit.objects.count(), 1)
        self.assertEqual(Physician.objects.count(), 1)
        self.assertEqual(Patient.objects.count(), 1)
        self.assertEqual(Device.objects.count(), 1)
        self.assertEqual(Clinic.objects.count(), 2)
        self.assertEqual(Clinic_Physician.objects.count(), 1)
        self.assertEqual(Patient_Physician.objects.count(), 1)
        self.assertEqual(Event.objects.count(), 1)

    def test_push_invalid_data(self):
        p1 = Patient()

        test_data = {
            "Patient": [
                {"firstName": "sehr", "uuid": str(p1.uuid)}
            ],
            "Patient_Physician": [
                {"uuid": str(uuid.uuid4()), "patient_uuid": str(p1.uuid),
                 "physician_uuid": "99999999-9999-9999-9999-999999999999"}
            ]
        }
        resp = self.client.post('/api/v1/sync/', self._enc(test_data),
                                HTTP_AUTHORIZATION="Bearer %s" % self.device.token)
        resp.verify(412)

    def test_push_undesirable_data(self):
        py1 = Physician()

        test_data = {
            "Physician": [
                {"uuid": str(py1.uuid), "key": "bob0bob0bob0bob0bob0bob0bob0bob0", "firstName": "garn",
                 "lastName": "nahel", "hashedPIN": "no?"}
            ]
        }
        resp = self.client.post('/api/v1/sync/', self._enc(test_data),
                                HTTP_AUTHORIZATION="Bearer %s" % self.device.token)
        resp.verify(201)
        # The system silently drops models not marked for external creation
        self.assertRaises(Physician.DoesNotExist, Physician.objects.get, uuid=py1.uuid)


class SyncSpecTestCase(BaseTestCase):
    def setUp(self):
        super(SyncSpecTestCase, self).setUp()
        self.resources = SynchronizedResource.__subclasses__()

    def test_preparer_sanity(self):
        """ Somewhat of a not-unit test to make sure there are no typos hidden in the API resources """
        # Enumerate all declared SynchronizedResources
        for synced_resource in self.resources:
            # Make sure it has the proper fieldspreparer
            assert synced_resource.preparer, "%s has no preparer" % synced_resource
            self.assertEqual(type(synced_resource.preparer), SynchronizedFieldsPreparer,
                             "%s has a preparer that isn't a SynchronizedFieldsPreparer" % synced_resource)
            # Take all the fields the model naturally has...
            model_fields = set(
                    [x.name for x in synced_resource.model._meta.fields + synced_resource.model._meta.many_to_many])
            # Plus the relations' IDs, placed under _id (NOT _uuid, despite the name of the database field...)
            model_fields |= set(["%s_id" % x.name for x in
                                 synced_resource.model._meta.fields + synced_resource.model._meta.many_to_many if
                                 hasattr(x.rel, "to")])
            # Get the fields specified in the preparer, excepting lambda expressions that we can't automagically check
            given_fields = set([x for x in synced_resource.preparer.fields.values() if not hasattr(x, "__call__")])
            # ...and make sure none are missing from the model
            self.assertEqual(given_fields - model_fields, set(),
                             "%s does not have fields %s specified in preparer - but it does have fields %s" % (
                                 synced_resource.model.__name__, given_fields - model_fields, model_fields))

    def test_missing_resources(self):
        """ Similarly, ensure there are no SynchronizedModels without matching SynchronizedResources """

        def all_subclasses(cls):
            return cls.__subclasses__() + [x for y in cls.__subclasses__() for x in all_subclasses(y)]

        # Check to make sure we didn't miss any SynchronizedModels entirely
        covered_models = set([x.model for x in self.resources])
        stranded_models = set([x for x in all_subclasses(SynchronizedModel) if not x._meta.abstract]) - covered_models
        self.assertEqual(stranded_models, set(),
                         "Missing SynchronizedResources for the following SynchronizedModels: %s" % stranded_models)
