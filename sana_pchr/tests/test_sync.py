from datetime import datetime, timedelta
from unittest.mock import patch

import pytz
from django.core.exceptions import ValidationError
from django.test import TestCase

from sana_pchr.models import Patient, Physician, Patient_Physician, Clinic, Device, Clinic_Physician
from sana_pchr.sync import SynchronizationProcessor, SerializedSynchronizationProcessor


class SynchronizationTestCase(TestCase):
    models = ["Patient", "Physician", "Patient_Physician"]

    def setUp(self):
        self.c1 = Clinic.objects.create(name="TestClinic", synchronized=datetime(2000, 1, 1, tzinfo=pytz.utc))
        self.d1 = Device.objects.create(clinic=self.c1, synchronized=datetime(2000, 1, 1, tzinfo=pytz.utc))

    def test_diff(self):
        ''' Test that we only sync objects from later timepoints'''
        sp = SynchronizationProcessor(self.d1, self.models)
        p1 = Patient.objects.create(firstName="roth", synchronized=datetime(2000, 1, 1, tzinfo=pytz.utc))
        p2 = Patient.objects.create(firstName="wase", synchronized=datetime(2000, 1, 3, tzinfo=pytz.utc))
        py1 = Physician.objects.create(firstName='ilise', lastName='bhat', hashedPIN='1234',
                                       synchronized=datetime(2000, 1, 1, tzinfo=pytz.utc))
        Patient_Physician(patient=p1, physician=py1, synchronized=datetime(2000, 1, 1, tzinfo=pytz.utc)).save()
        Patient_Physician(patient=p2, physician=py1, synchronized=datetime(2000, 1, 1, tzinfo=pytz.utc)).save()
        Clinic_Physician(clinic=self.c1, physician=py1, synchronized=datetime(2000, 1, 1, tzinfo=pytz.utc)).save()
        # Turn QuerySet into patient objects
        result = sp.calculate_delta(datetime(2000, 1, 2, tzinfo=pytz.utc))
        result = [(x, list(y)) for (x, y) in result]

        self.assertEqual(result, [(Patient, [p2])])

    def test_merge_direct(self):
        sp = SynchronizationProcessor(self.d1, self.models)
        p1 = Patient.objects.create(firstName="roth")
        p1.firstName = "naris"
        p1.updated += timedelta(seconds=1)

        self.assertEqual(Patient.objects.get(uuid=p1.uuid).firstName, "roth")
        sp.apply_changes([p1])
        self.assertEqual(Patient.objects.get(uuid=p1.uuid).firstName, "naris")

    def test_merge_insert(self):
        sp = SynchronizationProcessor(self.d1, self.models)
        p1 = Patient(firstName="roth")

        self.assertRaises(Patient.DoesNotExist, Patient.objects.get, uuid=p1.uuid)
        sp.apply_changes([p1])
        self.assertEqual(Patient.objects.get(uuid=p1.uuid).firstName, "roth")

    def test_merge_insert_calls_hooks(self):
        sp = SynchronizationProcessor(self.d1, self.models)
        py1 = Physician(firstName="roth", lastName='bhat', hashedPIN='1234', recovery_answer="bob")

        sp.apply_changes([py1])
        assert (Physician.objects.get(uuid=py1.uuid).recovery_key.key is not None)

    def test_merge_insert_m2m(self):
        ''' Ensure we can insert M2M association objects '''
        sp = SynchronizationProcessor(self.d1, self.models)
        p1 = Patient(firstName="roth")
        py1 = Physician.objects.create(firstName='ilise')
        rel = Patient_Physician(patient=p1, physician=py1)
        sp.apply_changes([p1, rel])
        self.assertEqual(Patient.objects.get(uuid=p1.uuid).firstName, "roth")
        self.assertSequenceEqual(Patient.objects.get(uuid=p1.uuid).physicians.all(), [py1])

    def test_merge_insert_m2m_both_misordered(self):
        ''' Ensure that both sides of the M2M relationship can be inserted at once
            ...and that the relationship model can be provided before the model it references
        '''
        sp = SynchronizationProcessor(self.d1, self.models)
        p1 = Patient(firstName="roth")
        py1 = Physician(firstName='ilise', lastName='bhat', hashedPIN='1234')

        rel = Patient_Physician(patient=p1, physician=py1)

        sp.apply_changes([p1, rel, py1])
        self.assertEqual(Patient.objects.get(uuid=p1.uuid).firstName, "roth")
        self.assertEqual(Physician.objects.get(uuid=py1.uuid).firstName, "ilise")
        self.assertSequenceEqual(Patient.objects.get(uuid=p1.uuid).physicians.all(), [py1])

    def test_merge_insert_m2m_missing_fk(self):
        ''' Make sure the system rejects broken FK relationships '''
        sp = SynchronizationProcessor(self.d1, self.models)
        p1 = Patient(firstName="roth")
        py1 = Physician(firstName='ilise', lastName='bhat', hashedPIN='1234')

        rel = Patient_Physician(patient=p1, physician=py1)

        self.assertRaises(ValidationError, sp.apply_changes, [p1, rel])
        # Ensure nothing was saved
        self.assertRaises(Patient.DoesNotExist, Patient.objects.get, uuid=p1.uuid)
        self.assertRaises(Physician.DoesNotExist, Physician.objects.get, uuid=py1.uuid)

    def test_merge_discard(self):
        sp = SynchronizationProcessor(self.d1, self.models)
        p1 = Patient.objects.create(firstName="roth")
        p1.firstName = "naris"
        p1.updated -= timedelta(seconds=60)

        self.assertEqual(Patient.objects.get(uuid=p1.uuid).firstName, "roth")
        sp.apply_changes([p1])
        self.assertEqual(Patient.objects.get(uuid=p1.uuid).firstName, "roth")

    def test_merge_time_travel(self):
        sp = SynchronizationProcessor(self.d1, self.models)
        p1 = Patient.objects.create(firstName="roth")
        p1.firstName = "naris"
        p1.synchronized += timedelta(seconds=60)

        self.assertRaises(SynchronizationProcessor.SynchronizationException, sp.apply_changes, [p1])

    def test_merge_bad_data(self):
        sp = SynchronizationProcessor(self.d1, self.models)
        p1 = Patient.objects.create(firstName="roth")
        p1.firstName = None
        p1.synchronized += timedelta(seconds=60)

        self.assertRaises(ValidationError, sp.apply_changes, [p1])
        # Ensure we didn't save despite this
        self.assertEqual(Patient.objects.get(uuid=p1.uuid).firstName, "roth")

    def test_merge_bad_data_multiple(self):
        sp = SynchronizationProcessor(self.d1, self.models)
        p1 = Patient.objects.create(firstName="roth")
        p2 = Patient.objects.create(firstName="samsa")
        p1.firstName = None
        p1.synchronized += timedelta(seconds=60)
        p2.firstName = "gracie"
        p2.updated += timedelta(seconds=1)

        self.assertRaises(ValidationError, sp.apply_changes, [p2, p1])
        # Reject the entire update because of a single failure
        self.assertEqual(Patient.objects.get(uuid=p2.uuid).firstName, "samsa")
        self.assertEqual(Patient.objects.get(uuid=p1.uuid).firstName, "roth")

    def test_merge_multiple(self):
        sp = SynchronizationProcessor(self.d1, self.models)
        p1 = Patient.objects.create(firstName="roth")
        p2 = Patient.objects.create(firstName="samsa")
        p1.firstName = "naris"
        p1.updated += timedelta(seconds=1)

        p2.firstName = "gracie"
        p2.updated += timedelta(seconds=1)

        sp.apply_changes([p1, p2])
        self.assertEqual(Patient.objects.get(uuid=p1.uuid).firstName, "naris")
        self.assertEqual(Patient.objects.get(uuid=p2.uuid).firstName, "gracie")

    def test_merge_multiple_vary(self):
        sp = SynchronizationProcessor(self.d1, self.models)
        p1 = Patient.objects.create(firstName="roth")
        p2 = Patient.objects.create(firstName="samsa")
        p1.firstName = "naris"
        p1.updated += timedelta(seconds=1)

        p2.firstName = "gracie"
        p2.updated -= timedelta(seconds=1)

        sp.apply_changes([p1, p2])
        self.assertEqual(Patient.objects.get(uuid=p1.uuid).firstName, "naris")
        self.assertEqual(Patient.objects.get(uuid=p2.uuid).firstName, "samsa")


class SerializedSynchronizationProcessorTestCase(TestCase):
    def setUp(self):
        self.c1 = Clinic.objects.create(name="TestClinic")
        self.d1 = Device.objects.create(clinic=self.c1)

    def test_serialize(self):
        ''' Make sure the serialization wrapper doesn't light on fire '''
        ssp = SerializedSynchronizationProcessor(self.d1)
        py1 = Physician.objects.create(firstName='ilise', lastName='bhat', hashedPIN='1234')
        p1 = Patient.objects.create(firstName="roth")
        Patient_Physician(patient=p1, physician=py1).save()
        Clinic_Physician(clinic=self.c1, physician=py1).save()

        with patch("sana_pchr.sync.SynchronizationProcessor.calculate_delta", return_value=[(Patient, [p1])]):
            res = ssp.calculate_delta("the beginning of time")
            # Good enough for here
            # I don't really want to unit-test the individual serializations
            # ...and I'd rather defer that kind of stuff to the API tests where I can use approvals
            assert (hasattr(res, "keys"))

    def test_deserialize(self):
        ''' Ensure that existing records can be updated from their serialized counterparts '''
        ssp = SerializedSynchronizationProcessor(self.d1)
        p1 = Patient.objects.create(firstName="roth")
        mod_date = p1.updated + timedelta(seconds=5)
        with patch("sana_pchr.sync.SynchronizationProcessor.apply_changes") as patched_intake:
            ssp.apply_changes(
                    {"Patient": [{"uuid": str(p1.uuid), "firstName": "isa", "updated": mod_date.isoformat()}]})
            p1m = patched_intake.call_args[0][0][0]
            self.assertEqual(p1m.firstName, "isa")
            # The timestamp will get parsed when someone calls full_clean()
            # That's not really the purview of this wrapper - so just use the string
            self.assertEqual(p1m.updated, mod_date.isoformat())

    def test_deserialize_m2m(self):
        ''' Ensure that existing records can be updated from their serialized counterparts '''
        ssp = SerializedSynchronizationProcessor(self.d1)
        p1 = Patient.objects.create(firstName="roth")
        py1 = Physician.objects.create(firstName='ilise', lastName='bhat', hashedPIN='1234')
        rel = Patient_Physician(patient=p1, physician=py1)
        ssp.apply_changes({"Patient_Physician": [
            {"uuid": str(rel.uuid), "patient_uuid": str(rel.patient.uuid), "physician_uuid": str(rel.physician.uuid)}]})
        relm = Patient_Physician.objects.get(uuid=rel.uuid)
        self.assertEqual(relm.patient, p1)
        self.assertEqual(relm.physician, py1)

    def test_deserialize_insert(self):
        ''' Ensure that new records can be inserted from their serialized counterparts '''
        ssp = SerializedSynchronizationProcessor(self.d1)
        p1 = Patient()
        mod_date = p1.updated + timedelta(seconds=5)
        with patch("sana_pchr.sync.SynchronizationProcessor.apply_changes") as patched_intake:
            ssp.apply_changes({"Patient": [{"uuid": str(p1.uuid), "firstName": "isa", "updated": mod_date.isoformat(),
                                            "synchronized": "sure is handy thisll get deleted before parsing"}]})
            p1m = patched_intake.call_args[0][0][0]
            self.assertEqual(p1m.firstName, "isa")
            # The timestamp will get parsed when someone calls full_clean()
            # That's not really the purview of this wrapper - so just use the string
            self.assertEqual(p1m.updated, mod_date.isoformat())

    def test_deserialize_superfluous_fields(self):
        ''' Make sure you can't overwrite internals by specifying unusual field names - since we just paste them into __dict__ atm '''
        ssp = SerializedSynchronizationProcessor(self.d1)
        p1 = Patient()
        with patch("sana_pchr.sync.SynchronizationProcessor.apply_changes") as patched_intake:
            ssp.apply_changes({"Patient": [{"uuid": str(p1.uuid), "top_secret_field": "DROP ALL THE TABLES"}]})
            p1m = patched_intake.call_args[0][0][0]
            self.assertFalse(hasattr(p1m, "top_secret_field"))
