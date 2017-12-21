from django.db import models
from .base import SynchronizedModel
from .patient import Patient
from .visit_category import VisitCategory


class Visit(SynchronizedModel):
    category = models.ForeignKey(VisitCategory, db_column='category_uuid')
    patient = models.ForeignKey(Patient, db_column='patient_uuid')

    def __str__(self):
        return "Visit by %s on %s" % (self.patient, self.created.date())
