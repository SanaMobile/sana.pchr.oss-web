from django.db import models
from .base import SynchronizedModel
from .encounter_category import EncounterCategory
from .visit import Visit
from .device import Device
from .physician import Physician
from .clinic import Clinic, Clinic_Physician
from .patient import Patient_Physician


class Encounter(SynchronizedModel):
    category = models.ForeignKey(EncounterCategory, db_column='category_uuid')
    visit = models.ForeignKey(Visit, db_column='visit_uuid')
    physician = models.ForeignKey(Physician, db_column="physician_uuid")
    clinic = models.ForeignKey(Clinic, db_column="clinic_uuid")
    device = models.ForeignKey(Device, db_column="device_uuid")

    def __str__(self):
        return "Encounter by %s with %s at %s" % (self.visit.patient, self.physician, self.created)

    def save(self, *args, **kwargs):
        if self.clinic.physicians.filter(pk=self.physician.uuid).exists():
            pass
        else:
            Clinic_Physician(clinic=self.clinic, physician=self.physician).save()

        if self.visit.patient.physicians.filter(pk=self.physician.uuid).exists():
            pass
        else:
            Patient_Physician(patient=self.visit.patient, physician=self.physician).save()

        return super(Encounter, self).save(*args, **kwargs)
