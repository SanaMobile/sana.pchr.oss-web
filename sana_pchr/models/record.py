from django.db import models
from .base import SynchronizedModel
from .encounter import Encounter
from .record_category import RecordCategory


class Record(SynchronizedModel):
    encounter = models.ForeignKey(Encounter, db_column='encounter_uuid')
    category = models.ForeignKey(RecordCategory, db_column='category_uuid')
    value = models.CharField(max_length=255)
    comment = models.TextField(blank=True)
