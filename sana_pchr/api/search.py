from restless.data import Data
from restless.exceptions import NotFound

from sana_pchr.sync import SerializedSynchronizationProcessor
from .base import BaseResource



class SearchPatientResource(BaseResource):
    # Endpoint for record retrieval for purposes of searching for patients/clinicians outside of your clinic

    def _use_transport_encryption(self):
        from sana_pchr.settings import TRANSPORT_ENCRYPTION, DEBUG
        return TRANSPORT_ENCRYPTION and not (DEBUG and "no_transport_encryption" in self.request.GET)

    def list(self):
        if self.request.GET.__contains__('unhcr'):
            res = SerializedSynchronizationProcessor(self.device).search_patient_unhcr(self.request.GET['unhcr'])
        elif self.request.GET.__contains__('birthYear'):
            year = self.request.GET['birthYear']
            city = None
            first_name = None
            last_name = None
            gender = None
            if self.request.GET.__contains__('birthCity'):
                city = self.request.GET['birthCity']
            if self.request.GET.__contains__('firstName'):
                first_name = self.request.GET['firstName']
            if self.request.GET.__contains__('lastName'):
                last_name = self.request.GET['lastName']
            if self.request.GET.__contains__('gender'):
                gender = self.request.GET['gender']
            res = SerializedSynchronizationProcessor(self.device).search_patient(year, first_name, last_name, city, gender)
        else:
            raise NotFound()
        if self._use_transport_encryption():
            res = self.serializer.serialize(res).encode("utf-8")
            res = self.device.key.encrypt(res)
        return Data(res, should_prepare=False)

class SearchPhysicianResource(BaseResource):
    # Endpoint for record retrieval for purposes of searching for patients/clinicians outside of your clinic

    def _use_transport_encryption(self):
        from sana_pchr.settings import TRANSPORT_ENCRYPTION, DEBUG
        return TRANSPORT_ENCRYPTION and not (DEBUG and "no_transport_encryption" in self.request.GET)

    def list(self):
        if self.request.GET.__contains__('contact'):
            res = SerializedSynchronizationProcessor(self.device).search_physician_contact(
                    self.request.GET['contact']),
        elif self.request.GET.__contains__('add_physician'):
            res = SerializedSynchronizationProcessor(self.device).add_physician(self.request.GET['add_physician'])
        else:
            raise NotFound()
        return Data(res, should_prepare=False)
