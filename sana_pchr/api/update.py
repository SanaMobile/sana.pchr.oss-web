import urllib
import json

from django.conf import settings
from django.core.files.base import File
from django.db.models.fields.files import FileField, FieldFile
from django.http import HttpResponsePermanentRedirect

from restless.constants import OK, CREATED, ACCEPTED, NO_CONTENT
from restless.data import Data
from restless.preparers import Preparer, FieldsPreparer

from .base import BaseResource
from sana_pchr.models import InstalledApp, DefaultFuncs
from django.http import HttpResponse

from sana_pchr.models import Device
from sana_pchr.settings_base import *
from restless.exceptions import Unauthorized, NotFound

class UpdateResource(BaseResource):

    model = InstalledApp
    preparer = FieldsPreparer(fields={
        "version":"version",
        "device":"device.uuid",
        "pkg":"pkg",
        "checksum":"checksum",
    })

    def is_debug(self):
        return True
    
    def _authenticated(self):
        ''' Replicate BaseResource method on GET'''
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

    def is_authenticated(self):
        # We use the provisioning password
        return True

    def is_file(self,data):
        return isinstance(data, File) or isinstance(data, FieldFile) or isinstance(data,FileField) or (type(data) == bytes)

    def build_response(self, data, status=200):
        if self.is_file(data):
            return self.build_response_file(data,status=status)
        else:
             return super(UpdateResource, self).build_response(data, status=status)
    
    def build_response_file(self, data, status=200):
        # get the size and filename
        if isinstance(data, File) or isinstance(data, FieldFile) or isinstance(data,FileField):
            fname = data.name.split('/')[-1]
            content_length = data.size
        elif type(data) == bytes:
            fname = "update.apk"
            content_length = len(data)
            
        # Build the response
        response = HttpResponse(data,
            content_type='application/vnd.android.package-archive')
        response['Content-Disposition'] = 'attachment; filename=%s' % fname
        response['Content-Length'] = content_length
        response.status_code = status
        return response
    
    def serialize(self, method, endpoint, data):
        if data and not getattr(data, 'should_prepare', True): 
            # check if data has value set
            val = data.value if hasattr(data, 'value') else None
            # set  is None
            value = val if val else bytes()
            if self.is_file(value):
                return value
        return super(BaseResource, self).serialize(method, endpoint, data.value)
        
    def list(self):
        if not self._authenticated():
            raise Unauthorized
        self.device.lastUpdated = DefaultFuncs.getNow()
        self.device.save()
        # Fetch from the file server
        try:
            headers = {
                "Authorization": "Bearer " + settings.UPDATE_API_KEY
            }
            request = urllib.request.Request(
                url=settings.UPDATE_URL_REDIRECT,
                headers=headers
            )
            response = urllib.request.urlopen(request)
            value = response.read()
        except:
            value = bytes()
        return Data(value, should_prepare=False)

    def create(self):
        # Use the provisioning password to authenticate
        # self.provisioning_password = self.data["provisioning_password"] if "provisioning_password" in self.data else ""
        # if not DEVICE_PROVISIONING_PASSWORD == self.provisioning_password:
        #     raise Unauthorized()

        # Record the installed app version first
        self.device = Device.objects.get(uuid=self.data['device'])
        version = self.data['version']
        self.device.currentVersion = version
        self.device.save()
        # Record the installed version here
        try:
            iapp = InstalledApp.objects.get(device__uuid=self.device.uuid)
        except:
            iapp = InstalledApp.objects.create(device=self.device, version=version)
        # Initialize response to no-update
        result = {
                "version": "0",
                "device": self.device,
                "pkg": "update.apk",
                "checksum": "00000000000000000000000000000000",
            }
        # Rlay to the file server - uses POST to mimic pchr web app
        try:
            headers = {
                "Authorization": "Bearer " + settings.UPDATE_API_KEY
            }
            data = {"version":"latest"}
            request = urllib.request.Request(
                url=settings.UPDATE_URL_VERSION,
                headers=headers,
            )
            response = urllib.request.urlopen(request)
            encoding =response.info().get_param('charset') or 'utf-8'
            data = json.loads(response.read().decode(encoding))
            # load data from file server
            result["version"] = data.get("version","0")
            result["checksum"] = data.get("checksum", "00000000000000000000000000000000")
            result["pkg"] = data.get("pkg","update-error.apk")
        except:
            pass
        return Data(result, should_prepare=False)
