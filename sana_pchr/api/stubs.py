from .preparers import SynchronizedFieldsPreparer
from .base import SynchronizedResource
from sana_pchr.models import Device, Physician, Patient, Patient_Physician, Clinic, Clinic_Physician, Encounter, \
    EncounterCategory, Visit, VisitCategory, Record, RecordCategory, Test, TestCategory, Event
from sana_pchr.models.medication import *

class DeviceResource(SynchronizedResource):
    model = Device
    preparer = SynchronizedFieldsPreparer(fields={
        "name": "name",
        "deviceMAC": "deviceMAC",
        "clinic_uuid": "clinic_id"
    })


class PatientResource(SynchronizedResource):
    model = Patient
    preparer = SynchronizedFieldsPreparer(fields={
        'firstName': 'firstName',
        'lastName': 'lastName',
        'UNHCR': 'UNHCR',
        'birthYear': 'birthYear',
        'birthCity': 'birthCity',
        'picture': lambda v: v.picture.url if v.picture else None,
        'gender': 'gender',
        'phone': 'phone',
        'provider_id': 'provider_id'
    })


class PatientPhysicianResource(SynchronizedResource):
    model = Patient_Physician
    # Note that for this, and all FK fields, it auto-names the internal field to _id. The DB column is _uuid
    # I assume this is more efficient than x.uuid since relations are generally lazy-loaded
    preparer = SynchronizedFieldsPreparer(fields={
        'patient_uuid': 'patient_id',
        'physician_uuid': 'physician_id'
    })


class PhysicianResource(SynchronizedResource):
    model = Physician
    readonly_keys = ['key']
    allow_create = False
    preparer = SynchronizedFieldsPreparer(fields={
        'firstName': 'firstName',
        'lastName': 'lastName',
        'picture': lambda v: v.picture.url if v.picture else None,
        'phone': 'phone',
        'email': 'email',
        'type': 'type'
    })


class ClinicPhysicianResource(SynchronizedResource):
    model = Clinic_Physician
    preparer = SynchronizedFieldsPreparer(fields={
        'clinic_uuid': 'clinic_id',
        'physician_uuid': 'physician_id'
    })


class ClinicResource(SynchronizedResource):
    model = Clinic
    preparer = SynchronizedFieldsPreparer(fields={
        "name": "name",
        "latitude": "latitude",
        "longitude": "longitude",
        "language": "language"
    })


class EncounterResource(SynchronizedResource):
    model = Encounter
    preparer = SynchronizedFieldsPreparer(fields={
        "category_uuid": "category_id",
        "visit_uuid": "visit_id",
        "physician_uuid": "physician_id",
        "clinic_uuid": "clinic_id",
        "device_uuid": "device_id"
    })


class EncounterCategoryResource(SynchronizedResource):
    model = EncounterCategory
    preparer = SynchronizedFieldsPreparer(fields={
        "displayName": "displayName",
        "displayNameAr": "displayNameAr",
        "priority": "priority"
    })


class VisitResource(SynchronizedResource):
    model = Visit
    preparer = SynchronizedFieldsPreparer(fields={
        "category_uuid": "category_id",
        "patient_uuid": "patient_id"
    })


class VisitCategoryResource(SynchronizedResource):
    model = VisitCategory
    preparer = SynchronizedFieldsPreparer(fields={
        "displayName": "displayName",
        "displayNameAr": "displayNameAr",
        "priority": "priority"
    })


class RecordResource(SynchronizedResource):
    model = Record
    preparer = SynchronizedFieldsPreparer(fields={
        "encounter_uuid": "encounter_id",
        "category_uuid": "category_id",
        "value": "value",
        "comment": "comment"
    })


class RecordCategoryResource(SynchronizedResource):
    model = RecordCategory
    preparer = SynchronizedFieldsPreparer(fields={
        "displayName": "displayName",
        "displayNameAr": "displayNameAr",
        "recordType": "recordType",
        "resultDataType": "resultDataType",
        "priority": "priority"
    })


class TestResource(SynchronizedResource):
    model = Test
    preparer = SynchronizedFieldsPreparer(fields={
        "encounter_uuid": "encounter_id",
        "category_uuid": "category_id",
        "result": "result",
    })


class TestCategoryResource(SynchronizedResource):
    model = TestCategory
    preparer = SynchronizedFieldsPreparer(fields={
        "displayName": "displayName",
        "displayNameAr": "displayNameAr",
        "resultType": "resultType",
        "resultMin": "resultMin",
        "resultMax": "resultMax",
        "resultUnits": "resultUnits",
        "resultUnitsAr": "resultUnitsAr",
        "priority": "priority"
    })

class MedicationResource(SynchronizedResource):
    model = Medication
    preparer = SynchronizedFieldsPreparer(fields={
        "dose": "dose",
        "interval": "interval",
        "times": "times",
        "dose_unit_uuid": "dose_unit_id",
        "interval_unit_uuid": "interval_unit_id",
        "end_date": "end_date",
        "encounter_uuid": "encounter_id",
        "category_uuid": "category_id",
        "comment": "comment"
    })

class MedicationCategoryResource(SynchronizedResource):
    model = MedicationCategory
    preparer = SynchronizedFieldsPreparer(fields={
        "displayName": "displayName",
        "displayNameAr": "displayNameAr",
        "otherName": "otherName",
        "group_uuid": "group_id",
        "dose_default": "dose_default",
        "interval_default": "interval_default",
        'dose_unit_uuid': 'dose_unit_id',
        'interval_unit_uuid':'interval_unit_id',
        "times_default": "times_default",
        "interaction_warning": "interaction_warning",
        "priority": "priority"
    })

class MedicationGroupCategoryResource(SynchronizedResource):
    model = MedicationGroupCategory
    preparer = SynchronizedFieldsPreparer(fields={
        "displayName": "displayName",
        "displayNameAr": "displayNameAr",
        "priority": "priority"
    })

class DoseUnitCategoryResource(SynchronizedResource):
    model = DoseUnitCategory
    preparer = SynchronizedFieldsPreparer(fields={
        "displayName": "displayName",
        "displayNameAr": "displayNameAr",
        "priority": "priority"
    })

class IntervalUnitCategoryResource(SynchronizedResource):
    model = IntervalUnitCategory
    preparer = SynchronizedFieldsPreparer(fields={
        "displayName": "displayName",
        "displayNameAr": "displayNameAr",
        "priority": "priority"
    })
    
class EventResource(SynchronizedResource):
    model = Event
    preparer = SynchronizedFieldsPreparer(fields={
        "user": "user",
        "device": "device",
        "clinic": "clinic",
        "status": "status",
        "code": "code",
        "message": "message",
        "exception": "exception"
    })
