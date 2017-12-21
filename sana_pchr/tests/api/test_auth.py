from unittest.mock import patch, Mock

from sana_pchr.models import Device, Physician, Clinic, Clinic_Physician
from sana_pchr.settings import DEVICE_PROVISIONING_PASSWORD
from .base import BaseTestCase
from .utils import deterministic_uuids


class ProvisioningResourceTestCase(BaseTestCase):
    def test_incorrect_password(self):
        resp = self.client.post('/api/v1/auth/provision')
        resp.verify(401)

    def test_missing_fields(self):
        resp = self.client.post('/api/v1/auth/provision', {"provisioning_password": DEVICE_PROVISIONING_PASSWORD})
        resp.verify(412)

    def test_successful_provision(self):
        resp = self.client.post('/api/v1/auth/provision',
                                {"provisioning_password": DEVICE_PROVISIONING_PASSWORD, "name": "gracie",
                                 "deviceMAC": "zz:zz:zz:zz:zz"})
        resp.verify(201)

    def test_dupe_provision(self):
        resp = self.client.post('/api/v1/auth/provision',
                                {"provisioning_password": DEVICE_PROVISIONING_PASSWORD, "name": "gracie",
                                 "deviceMAC": "zz:zz:zz:zz:zz"})
        resp_2 = self.client.post('/api/v1/auth/provision',
                                  {"provisioning_password": DEVICE_PROVISIONING_PASSWORD, "name": "gracie update",
                                   "deviceMAC": "zz:zZ:zZ:zz:zz"})

        resp.verify(201, "create_original")
        resp_2.verify(201, "create_dupe")
        self.assertEqual(resp.content, resp_2.content.replace(b'gracie update', b'gracie'))


class CredentialsResourceTestCase(BaseTestCase):
    def test_no_auth(self):
        resp = self.client.get('/api/v1/auth/credentials')
        resp.verify(401)

    @patch('os.urandom', Mock(side_effect=lambda x: b'q' * x))
    @patch('django.contrib.auth.hashers.BasePasswordHasher.salt', Mock(side_effect=lambda: "SALT"))
    def setUp(self):
        super(CredentialsResourceTestCase, self).setUp()
        self.uuid_gen = deterministic_uuids()
        with patch('uuid.uuid4', side_effect=self.uuid_gen):
            d1 = Device.objects.create(deviceMAC="00:00:00:00")
            p1 = Physician.objects.create(firstName="santahm", lastName="tuhan", recovery_question="1+1",
                                          recovery_answer="-2")
            c1 = Clinic.objects.create(name="c1")
            c2 = Clinic.objects.create(name="c2")
            p2 = Physician.objects.create(firstName="p2", lastName="tuhan", recovery_question="1+1",
                                          recovery_answer="-2")
            Clinic_Physician(clinic=c1, physician=p1).save()
            Clinic_Physician(clinic=c2, physician=p2).save()
            d1.clinic = c2

    @patch('os.urandom', Mock(side_effect=lambda x: b'q' * x))
    def test_credentials_getclinics(self):
        params = ({"clinic": 1})
        with patch('uuid.uuid4', side_effect=self.uuid_gen):
            d = Device.objects.create()
        resp = self.client.get('/api/v1/auth/credentials', params, HTTP_AUTHORIZATION="Bearer %s" % d.token)
        resp.verify(200)

    @patch('os.urandom', Mock(side_effect=lambda x: b'q' * x))
    def test_credentials_setclinic(self):
        with patch('uuid.uuid4', side_effect=self.uuid_gen):
            dev = Device.objects.create(deviceMAC="123")
            params = ({"setclinic": Clinic.objects.get(name="c1").uuid})
            resp = self.client.get('/api/v1/auth/credentials', params, HTTP_AUTHORIZATION="Bearer %s" % dev.token)
            resp.verify(200)

            self.assertEqual(Device.objects.get(deviceMAC="123").clinic, Clinic.objects.get(name="c1"))

    @patch('os.urandom', Mock(side_effect=lambda x: b'q' * x))
    def test_credentials_list(self):
        with patch('uuid.uuid4', side_effect=self.uuid_gen):
            dev = Device(deviceMAC="wHAHHAHA", clinic=Clinic.objects.get(name="c1"))
        dev.save()
        resp = self.client.get('/api/v1/auth/credentials', HTTP_AUTHORIZATION="Bearer %s" % dev.token)
        resp.verify(200)

    @patch('os.urandom', Mock(side_effect=lambda x: b'q' * x))
    def test_credentials_list_empty_device(self):
        with patch('uuid.uuid4', side_effect=self.uuid_gen):
            d = Device.objects.create()
        resp = self.client.get('/api/v1/auth/credentials', HTTP_AUTHORIZATION="Bearer %s" % d.token)
        resp.verify(200)
