import base64
from restless.exceptions import Unauthorized
from restless.preparers import FieldsPreparer

from sana_pchr.forms import DeviceForm
from sana_pchr.models import Physician, Device, Clinic
from sana_pchr.settings import DEVICE_PROVISIONING_PASSWORD
from .base import BaseResource
from .exceptions import ValidationError
from datetime import datetime
import pytz

class ProvisioningResource(BaseResource):
    # This stuff isn't, strictly speaking, REST
    # But it's close enough
    preparer = FieldsPreparer(fields={
        'uuid': 'uuid',
        'name': 'name',
        'token': 'token',
        'deviceMAC': 'deviceMAC'
    })

    def is_authenticated(self):
        # We use the provisioning password
        return True

    def create(self):
        provisioning_password = self.data["provisioning_password"] if "provisioning_password" in self.data else ""
        if DEVICE_PROVISIONING_PASSWORD != provisioning_password:
            raise Unauthorized()

        form = DeviceForm(self.data)
        if form.is_valid():
            try:
                form = DeviceForm(self.data, instance=Device.objects.get(deviceMAC=form.cleaned_data["deviceMAC"]))
            except Device.DoesNotExist:
                pass
            return form.save()
        else:
            raise ValidationError(form.errors)


class CredentialsResource(BaseResource):

    @staticmethod
    def serialize_physicians(device, physicians):
        users_collection = []
        for physician in physicians:

            phys_obj = {
                "uuid": physician.uuid,
                "firstName": physician.firstName,
                "lastName": physician.lastName,
                "picture": physician.picture.url if physician.picture else None,
                "recovery_question": physician.recovery_question,
                "device_key_user_key": base64.b64encode(physician.key.encrypt(device.key.key)).decode(
                        "ascii"),
                "recovery_device_key": physician.recovery_key.encrypt(device.key.key),
                "recovery_salt": base64.b64encode(device.key.encrypt(physician.recovery_key.salt.encode("ascii"))).decode("ascii"),
                "hashedPIN_user_key": base64.b64encode(
                        physician.key.encrypt(physician.hashedPIN.encode("ascii"))).decode("ascii"),
                "deleted": physician.deleted,
                "synchronized": physician.synchronized,
                "created": physician.created,
                "updated": physician.updated,
                "type": physician.type

            }

            if physician.recovery_key:
                phys_obj["device_key_recovery_key"] = physician.recovery_key.encrypt(device.key.key)
                phys_obj["hashedPIN_recovery_key"] = physician.recovery_key.encrypt(
                        physician.hashedPIN.encode("ascii"))

            users_collection.append(phys_obj)
        return users_collection

    def list(self):
        users_collection = []
        if self.request.GET.__contains__('clinic'):
            for clinic in Clinic.objects.all():
                clin_obj = {
                    "uuid": clinic.uuid,
                    "name": clinic.name,
                    "longitude": clinic.longitude,
                    "latitude": clinic.latitude,
                    "language": clinic.language,
                }
                users_collection.append(clin_obj)
        else:

            if self.request.GET.__contains__('setclinic'):
                set_clinic = self.request.GET['setclinic']

                self.device.clinic = Clinic.objects.get(uuid=set_clinic)
                self.device.updated = datetime.utcnow().replace(tzinfo=pytz.utc)
                self.device.synchronized = datetime.utcnow().replace(tzinfo=pytz.utc)
                self.device.save()
            if self.device.clinic:
                physicians = Physician.objects.filter(clinic_physician__clinic=self.device.clinic)
                users_collection=self.serialize_physicians(self.device, physicians)
        return users_collection

