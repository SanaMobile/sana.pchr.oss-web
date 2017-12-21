from django.db import models
from .base import SynchronizedModel
from .encounter import Encounter
from .test_category import TestCategory


class Test(SynchronizedModel):
    encounter = models.ForeignKey(Encounter, db_column='encounter_uuid')
    category = models.ForeignKey(TestCategory, db_column='category_uuid')
    result = models.CharField(max_length=1023)
