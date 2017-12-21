from django.db import models
from django.utils.translation import ugettext as _

from .base import SynchronizedModel
from .clinic import Clinic
from .device import Device

__all__ = [
    "Event"
    ]

class Event(SynchronizedModel):
    user =  models.CharField(max_length=36, blank=False)
    device =  models.CharField(max_length=36, blank=False)
    clinic =  models.CharField(max_length=36, blank=False)
    status =  models.CharField(max_length=16, blank=False)
    code =  models.CharField(max_length=64, blank=False)
    message =  models.CharField(max_length=127, blank=True)
    exception =  models.CharField(max_length=127, blank=True)
    
    def clinic_str(self):
        if self.clinic:
            try:
                return Clinic.objects.get(uuid=self.clinic).__str__()
            except:
                return _("Not Found")
        else:
            return _("Unknown")
    
    def device_str(self):
        if self.device:
            try:
                return Device.objects.get(uuid=self.device).__str__()
            except:
                return _("Not Found")
        else:
            return _("Unknown")
