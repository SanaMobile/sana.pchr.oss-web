import json
from datetime import datetime
from unittest.mock import patch, Mock

import pytz

from sana_pchr.models import *
from sana_pchr.models.medication import *
from .base import BaseTestCase
from .utils import deterministic_uuids


class SearchTestCase(BaseTestCase):
    '''Tests methods for retrieval of records for people outside of the device's clinic'''
    models = ["Patient", "Physician", "Patient_Physician"]

    @patch('os.urandom', Mock(side_effect=lambda x: b'q' * x))
    @patch('django.contrib.auth.hashers.BasePasswordHasher.salt', Mock(side_effect=lambda: "SALT"))
    def setUp(self):
        super(SearchTestCase, self).setUp()
        self.now = datetime.utcnow().replace(tzinfo=pytz.utc)
        self.uuid_gen = deterministic_uuids()
        with patch('uuid.uuid4', side_effect=self.uuid_gen):
            self.clinic = Clinic.objects.create(name="cinilC")
            self.clinic2 = Clinic.objects.create(name="Clinic2")
            self.device = Device.objects.create(name="deviceecived", clinic=self.clinic)
            self.device2 = Device.objects.create(name="whoops", clinic=self.clinic2)
            self.p1 = Patient.objects.create(firstName="Bob", UNHCR='12345678', lastName="Smith", birthYear=1950, birthCity="Boston")
            self.p2 = Patient.objects.create(firstName="Rob", UNHCR='23456789', lastName="Smith", birthYear=1948, birthCity="Boston")
            self.p3 = Patient.objects.create(firstName="Cob", UNHCR='23456789', lastName="Smith", birthYear=1948, birthCity="Coston")
            self.py1 = Physician.objects.create(firstName='ilise', lastName='bhat', email='ilise@med.com',
                                                phone='1234 5678', hashedPIN='1234', recovery_question = 'Alo', recovery_answer='ha')
            self.py2 = Physician.objects.create(firstName='elise', lastName='bhat', email='elise@med.com',
                                                phone='2345 6789', hashedPIN='1234', recovery_question = 'Alo', recovery_answer='ha')
            self.vc1 = VisitCategory.objects.create()
            self.ec1 = EncounterCategory.objects.create()
            self.rc1 = RecordCategory.objects.create(recordType=1)
            self.tc1 = TestCategory.objects.create(resultType=1)
            self.v1 = Visit.objects.create(category=self.vc1, patient=self.p1)
            self.e1 = Encounter.objects.create(category=self.ec1, physician=self.py1, clinic=self.clinic,
                                               device=self.device, visit=self.v1)
            self.r1 = Record.objects.create(value="Testing 123", category=self.rc1, encounter=self.e1)
            self.t1 = Test.objects.create(result="47", category=self.tc1, encounter=self.e1)

            self.iu1 = IntervalUnitCategory.objects.create(displayName="day")
            self.du1 = DoseUnitCategory.objects.create(displayName="pill")
            self.mg1 = MedicationGroupCategory.objects.create(displayName="statin")
            self.mc1 = MedicationCategory.objects.create(displayName="Lipitor", otherName="atorvastatin", group=self.mg1,
                                          dose_default=1, interval_default=2, times_default=3, dose_unit=self.du1,
                                          interval_unit=self.iu1)


            self.m1 = Medication.objects.create(category=self.mc1, interval=1, dose=2, times=3, dose_unit=self.du1,
                                                interval_unit=self.iu1, end_date=date(2016,2,3), encounter=self.e1)

            Clinic_Physician(clinic=self.clinic, physician=self.py1).save()
            Clinic_Physician(clinic=self.clinic2, physician=self.py2).save()

    def test_add_patient_uuid(self):
        '''Retrieve patient via uuid'''

        params = {'no_transport_encryption': 1, 'add_patient': self.p1.uuid, 'physician': self.py2.uuid}
        resp = self.client.get('/api/v1/sync/', params, HTTP_AUTHORIZATION="Bearer %s" % self.device2.token)

        resp.verify(200)

        self.assertEqual(Patient_Physician.objects.filter(patient=self.p1, physician=self.py2).exists(), True)


    @patch('os.urandom', Mock(side_effect=lambda x: b'q' * x))
    @patch('django.contrib.auth.hashers.BasePasswordHasher.salt', Mock(side_effect=lambda: "SALT"))
    def test_add_patient_bad_uuid(self):
        '''Retrieving patient records by uuid: Make sure error is returned if given uuids are bad'''
        params = {'no_transport_encryption': 1, 'add_patient': self.p1.uuid, 'physician': 'Not a uuid'}

        resp = self.client.get('/api/v1/sync/', params, HTTP_AUTHORIZATION="Bearer %s" % self.device2.token)

        resp.verify(404)

        self.assertEqual(Patient_Physician.objects.count(), 1)

    @patch('os.urandom', Mock(side_effect=lambda x: b'q' * x))
    @patch('django.contrib.auth.hashers.BasePasswordHasher.salt', Mock(side_effect=lambda: "SALT"))
    def test_add_physician_uuid(self):
        '''Retrieving all records belonging to a physician'''
        params = {'add_physician': self.py1.uuid}
        resp = self.client.get('/api/v1/sync/', params, HTTP_AUTHORIZATION="Bearer %s" % self.device2.token)

        resp.verify(200)

        self.assertEqual(Clinic_Physician.objects.filter(clinic=self.clinic2, physician=self.py1).exists(), True)

    @patch('os.urandom', Mock(side_effect=lambda x: b'q' * x))
    @patch('django.contrib.auth.hashers.BasePasswordHasher.salt', Mock(side_effect=lambda: "SALT"))
    def test_add_physician_bad_uuid(self):
        '''Retrieving all records belonging to a physician, make sure bad uuid gives 404'''
        params = {'no_transport_encryption': 1, 'add_physician': "ladeeda"}
        resp = self.client.get('/api/v1/sync/', params, HTTP_AUTHORIZATION="Bearer %s" % self.device2.token)

        resp.verify(404)

        self.assertEqual(Clinic_Physician.objects.count(), 2)

    @patch('os.urandom', Mock(side_effect=lambda x: b'q' * x))
    @patch('django.contrib.auth.hashers.BasePasswordHasher.salt', Mock(side_effect=lambda: "SALT"))
    def test_search_physician_contact_email(self):
        '''Search for physician by email'''
        params = {'contact': "ilise@med.com"}
        resp = self.client.get('/api/v1/search/physician/', params, HTTP_AUTHORIZATION="Bearer %s" % self.device2.token)

        resp.verify(200)

    @patch('os.urandom', Mock(side_effect=lambda x: b'q' * x))
    @patch('django.contrib.auth.hashers.BasePasswordHasher.salt', Mock(side_effect=lambda: "SALT"))
    def test_search_physician_contact_bad_email(self):
        '''Search for physician by email,bad email to 404'''
        params = {'contact': "nomail@med.com"}
        resp = self.client.get('/api/v1/search/physician/', params, HTTP_AUTHORIZATION="Bearer %s" % self.device2.token)

        resp.verify(404)

    @patch('os.urandom', Mock(side_effect=lambda x: b'q' * x))
    @patch('django.contrib.auth.hashers.BasePasswordHasher.salt', Mock(side_effect=lambda: "SALT"))
    def test_search_physician_contact_phone(self):
        '''Search for physician by phone'''
        params = {'contact': "1234 5678"}
        resp = self.client.get('/api/v1/search/physician/', params, HTTP_AUTHORIZATION="Bearer %s" % self.device2.token)

        resp.verify(200)

    @patch('os.urandom', Mock(side_effect=lambda x: b'q' * x))
    @patch('django.contrib.auth.hashers.BasePasswordHasher.salt', Mock(side_effect=lambda: "SALT"))
    def test_search_physician_contact_bad_phone(self):
        '''Search for physician by phone, makes sure bad phone# gives 404'''
        params = {'contact': "not a number"}
        resp = self.client.get('/api/v1/search/physician/', params, HTTP_AUTHORIZATION="Bearer %s" % self.device2.token)

        resp.verify(404)

    def test_search_patient_encrypted(self):
        '''Make sure patient search endpoint is encrypted'''
        params = {'unhcr': "23456789"}
        resp = self.client.get('/api/v1/search/patient/', params, HTTP_AUTHORIZATION="Bearer %s" % self.device2.token)
        json.loads(self.device2.key.decrypt(resp.content).decode("utf-8"))

    def test_search_patient_unhcr(self):
        '''Search for patients by unhcr id'''
        params = {'no_transport_encryption': 1, 'unhcr': "23456789"}
        resp = self.client.get('/api/v1/search/patient/', params, HTTP_AUTHORIZATION="Bearer %s" % self.device2.token)

        resp.verify(200)

    def test_search_patient_bad_unhcr(self):
        '''Search for patients by unhcr id, bad unhcr to 404'''
        params = {'no_transport_encryption': 1, 'unhcr': "not valid at all"}
        resp = self.client.get('/api/v1/search/patient/', params, HTTP_AUTHORIZATION="Bearer %s" % self.device2.token)

        resp.verify(404)

    def test_search_patient_year(self):
        '''Search for patients by year'''
        params = {'no_transport_encryption': 1, 'birthYear': "1948"}
        resp = self.client.get('/api/v1/search/patient/', params, HTTP_AUTHORIZATION="Bearer %s" % self.device2.token)

        resp.verify(200)

    def test_search_patient_year_other_fields(self):
        '''Search for patients by year and the beginning parts of other fields '''
        params = {'no_transport_encryption': 1, 'birthYear': "1948", 'lastName': 'Sm', 'birthCity': 'C'}
        resp = self.client.get('/api/v1/search/patient/', params, HTTP_AUTHORIZATION="Bearer %s" % self.device2.token)

        resp.verify(200)

        params = {'no_transport_encryption': 1, 'birthYear': "1948", 'firstName': 'C'}
        resp = self.client.get('/api/v1/search/patient/', params, HTTP_AUTHORIZATION="Bearer %s" % self.device2.token)

        resp.verify(200)

    def test_search_patient_blank_fields(self):
        '''make sure blank fields raise 404s'''
        params = {'no_transport_encryption': 1, 'unhcr': ""}
        resp = self.client.get('/api/v1/search/patient/', params, HTTP_AUTHORIZATION="Bearer %s" % self.device2.token)

        resp.verify(404)

        params = {'no_transport_encryption': 1, 'birthYear': ""}
        resp = self.client.get('/api/v1/search/patient/', params, HTTP_AUTHORIZATION="Bearer %s" % self.device2.token)

        resp.verify(404)

        params = {'no_transport_encryption': 1, 'mumboJumbo': ""}
        resp = self.client.get('/api/v1/search/patient/', params, HTTP_AUTHORIZATION="Bearer %s" % self.device2.token)

        resp.verify(404)

