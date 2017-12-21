from django.db import models

from .base import SynchronizedModel, SynchronizedThroughModel
from .physician import Physician


class Clinic(SynchronizedModel):
    name = models.CharField(max_length=45)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    language = models.CharField(max_length=2, default="ar");

    physicians = models.ManyToManyField(Physician, through="Clinic_Physician", blank=True)

    def __str__(self):
        return "%s clinic" % self.name


class Clinic_Physician(SynchronizedThroughModel):
    clinic = models.ForeignKey(Clinic, db_column="clinic_uuid", null=False, blank=False)
    physician = models.ForeignKey(Physician, db_column="physician_uuid", null=False, blank=False)

    def __init__(self, *args, **kwargs):
        super(Clinic_Physician, self).__init__(*args, **kwargs)
        try:
            if self.clinic:
                if self.physician:
                    self.uuid = self.clinic_id[0:15] + self.physician_id[0:15]
        except models.ObjectDoesNotExist:
            pass

    def save(self, *args, **kwargs):
        self.uuid = self.clinic.uuid[0:15] + self.physician.uuid[0:15]
        return super(Clinic_Physician, self).save(*args, **kwargs)

    def __str__(self):
        return self.physician.__str__() + " " + self.clinic.__str__()
