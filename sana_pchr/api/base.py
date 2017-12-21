from restless.dj import DjangoResource
from restless.utils import format_traceback
from .serializers import AugmentedJSONSerializer
from .preparers import SynchronizedFieldsPreparer
from sana_pchr.models import Device
import six
import sys


class BaseResource(DjangoResource):
    serializer = AugmentedJSONSerializer()

    def is_authenticated(self):
        bearer_token = self.request.META.get("HTTP_AUTHORIZATION", None)
        if not bearer_token:
            return False
        # Authorization: Bearer #####
        device_token = bearer_token.split(' ')[1]
        try:
            self.device = Device.objects.get(token=device_token)
        except Device.DoesNotExist:
            return False
        else:
            return True

    def wrap_list_response(self, data):
        # There's a rather obscure XSS exploit wrapping the return value in a dict solves, which is what restless does
        return data

    def deserialize(self, method, endpoint, body):
        try:
            return super(BaseResource, self).deserialize(method, endpoint, body)
        except UnicodeDecodeError:
            return body

    def serialize(self, method, endpoint, data):
        if data and not getattr(data, 'should_prepare', True) and type(data.value) == bytes:
            return data.value
        return super(BaseResource, self).serialize(method, endpoint, data)

    # Restless's built-in error object is rather cut-and-run
    def build_error(self, err):
        data = {
        }

        if hasattr(err, "data"):
            data['error'] = err.data
        else:
            data['error'] = six.text_type(err)

        if self.is_debug():
            # Add the traceback.
            data['traceback'] = format_traceback(sys.exc_info())

        body = self.serializer.serialize(data)
        status = getattr(err, 'status', 500)
        return self.build_response(body, status=status)


class SynchronizedResource(BaseResource):
    preparer = SynchronizedFieldsPreparer()
    # The underscore variants because I really dont want these to accidentally get overwritten
    # The sync appends the two for handling
    allow_create = True
    allow_update = True
    # Which keys to block from being updated in all cases
    _readonly_keys = ['synchronized']
    readonly_keys = []
    # Which keys to block during updates (but allow during creation)
    _readonly_update_keys = ['uuid']
    readonly_update_keys = []
