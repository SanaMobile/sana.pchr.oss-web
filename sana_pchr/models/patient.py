import uuid

import base64
from django.db import models

from .base import SynchronizedModel, SynchronizedThroughModel
from .physician import Physician


class Patient(SynchronizedModel):
    firstName = models.CharField(max_length=45, blank=False, db_index=True)
    lastName = models.CharField(max_length=45, blank=True, db_index=True)
    UNHCR = models.CharField(max_length=45, blank=True, db_index=True)
    birthYear = models.CharField(max_length=45, blank=True, db_index=True)
    birthCity = models.CharField(max_length=45, blank=True, db_index=True)
    picture = models.ImageField(blank=True)
    physicians = models.ManyToManyField(Physician, through='Patient_Physician')
    gender = models.CharField(max_length=1, default='M')
    #phone num
    phone = models.CharField(max_length=25, blank=True, db_index=True)
    provider_id = models.CharField(max_length=45, blank=True, db_index=True)

    def __str__(self):
        return "%s %s" % (self.firstName, self.lastName)

    @property
    def qr_contents(self):
        # Had to make this base64-encoded because none all of the Android QR scanning libraries could stomach the raw binary
        # Maybe in the future it can be switched back - hence the leading NULL for differentiation.
        return base64.b64encode(b"\0" + uuid.UUID(self.uuid).bytes)


class Patient_Physician(SynchronizedThroughModel):
    patient = models.ForeignKey(Patient, db_column="patient_uuid", null=False, blank=False)
    physician = models.ForeignKey(Physician, db_column="physician_uuid", null=False, blank=False)

    def __init__(self, *args, **kwargs):
        super(Patient_Physician, self).__init__(*args, **kwargs)
        try:
            if self.patient:
                if self.physician:
                    self.uuid = self.patient.uuid[0:15] + self.physician.uuid[0:15]
        except models.ObjectDoesNotExist:
            pass

    def save(self, *args, **kwargs):
        self.uuid = self.patient_id[0:15] + self.physician_id[0:15]
        return super(Patient_Physician, self).save(*args, **kwargs)

    def __str__(self):
        return self.physician.__str__() + " " + self.patient.__str__()
