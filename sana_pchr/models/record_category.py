from django.db import models
from .base import CategoryModel


class RecordCategory(CategoryModel):
    recordType = models.IntegerField()
    resultDataType = models.CharField(max_length=45, blank=True)
