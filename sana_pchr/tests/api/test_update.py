from unittest.mock import patch, Mock

from sana_pchr.models import App
from sana_pchr.settings import DEVICE_PROVISIONING_PASSWORD
from .base import BaseTestCase

class UpdateResourceTestCase(BaseTestCase):
    def test_no_auth(self):
        resp = self.client.get('/app/update/')
        resp.verify(401)

    def setUp(self):
        super(AppResourceTestCase, self).setUp()
