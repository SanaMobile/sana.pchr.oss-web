from django.db import models
from .fields import CredentialField, DefaultFuncs
from .base import SynchronizedModel
from .clinic import Clinic
from datetime import date


class Device(SynchronizedModel):
    name = models.CharField(max_length=45, blank=False)
    deviceMAC = models.CharField(max_length=17, blank=False)
    key = CredentialField(blank=False)
    token = models.CharField(max_length=32, blank=False, default=DefaultFuncs.make_uuid)
    clinic = models.ForeignKey(Clinic, db_column='clinic_uuid', blank=True, null=True)
    lastSynchronized = models.DateTimeField(default=DefaultFuncs.getNow)
    lastUpdated = models.DateField(default=DefaultFuncs.getNow)
    currentVersion = models.CharField(max_length=3, blank=True)

    def __str__(self):
        return "%s (%s)" % (self.name, self.deviceMAC)
