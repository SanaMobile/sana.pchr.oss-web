from django.db import models
from .base import CategoryModel


class TestCategory(CategoryModel):
    resultType = models.IntegerField()
    resultMin = models.FloatField(default = 0,blank=False)
    resultMax = models.FloatField(default = 1000, blank=False)
    resultUnits = models.CharField(max_length=127, blank=True, null=True)
    resultUnitsAr = models.CharField(max_length=127, blank=True, null=True)

