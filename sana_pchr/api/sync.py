from .exceptions import ValidationError
from django.core.exceptions import ValidationError as DjValidationError
from .base import BaseResource
import dateutil.parser
from sana_pchr.sync import SerializedSynchronizationProcessor
from sana_pchr.crypto import Credential
from restless.data import Data
from restless.exceptions import Unauthorized, NotFound
import pytz

class SyncResource(BaseResource):
    # OK, I admit absolutely nothing in this application is actually REST
    # This endpoint the least so

    def _use_transport_encryption(self):
        from sana_pchr.settings_base import TRANSPORT_ENCRYPTION, DEBUG
        return TRANSPORT_ENCRYPTION and not (DEBUG and "no_transport_encryption" in self.request.GET)

    def list(self):
        if self.request.GET.__contains__('synchronized_after'):
            datestring = self.request.GET["synchronized_after"]
            datestring = datestring.replace(" ", "+")
            synchronized_after_ts = dateutil.parser.parse(datestring)
            if not synchronized_after_ts.tzinfo:
                synchronized_after_ts = pytz.utc.localize(synchronized_after_ts)
            res = SerializedSynchronizationProcessor(self.device).calculate_delta(synchronized_after_ts)
        elif self.request.GET.__contains__('add_patient'):
            res = SerializedSynchronizationProcessor(self.device).add_patient(self.request.GET['add_patient'],
                                                                              self.request.GET['physician'])
        elif self.request.GET.__contains__('add_physician'):
            res = SerializedSynchronizationProcessor(self.device).add_physician(self.request.GET['add_physician'])
            return Data(res, should_prepare=False)
        else:
            raise NotFound()
        if self._use_transport_encryption():
            res = self.serializer.serialize(res).encode("utf-8")
            res = self.device.key.encrypt(res)
        return Data(res, should_prepare=False)

    def create(self):
        if self._use_transport_encryption():
            try:
                data = self.serializer.deserialize(self.device.key.decrypt(self.data))
            except Credential.AuthenticationException:
                raise Unauthorized()
        else:
            data = self.data
        try:
            SerializedSynchronizationProcessor(self.device).apply_changes(data)
        except DjValidationError as e:
            # This isn't the best - they'll see messages associated with field names, but not the model of that field
            # But, requestors should probably get it right on the first try and not have to rely on the error message programatically
            raise ValidationError(e)
