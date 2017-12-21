from django.db import models
from .base import CategoryModel, SynchronizedModel
from .encounter import Encounter


# e.g. thiazide diuretics, etc.
class MedicationGroupCategory(CategoryModel):
    pass


# e.g. mg, pill
class DoseUnitCategory(CategoryModel):
    pass


# e.g day, week, hour
class IntervalUnitCategory(CategoryModel):
    pass

class MedicationCategory(CategoryModel):
    #Drug name
    otherName = models.CharField(max_length=256, null=True, blank=True)
    abbrev = models.CharField(max_length=10, blank=True)
    # Medication group describes what kind of drug: anti-hypertensive? etc.
    group = models.ForeignKey(MedicationGroupCategory, db_column='group_uuid')
    dose_default = models.FloatField(blank=True, null=True)
    interval_default = models.FloatField(blank=True, null=True)
    dose_unit = models.ForeignKey(DoseUnitCategory, db_column='dose_unit_uuid', null=True, blank=True)
    interval_unit = models.ForeignKey(IntervalUnitCategory, db_column='interval_unit_uuid', null=True, blank=True)
    times_default = models.IntegerField(blank=True, null=True)
    interaction_warning = models.CharField(max_length=255, blank=True, null=True)


class Medication(SynchronizedModel):
    # Dosages are described in the form
    # dose dose_unit times times per interval interval_unit
    # 1    pill        3   times per 1        day
    category = models.ForeignKey(MedicationCategory, db_column="category_uuid")

    dose = models.FloatField(blank=True, null=True)
    interval = models.IntegerField(blank=True, null=True)
    times = models.IntegerField(blank=True, null=True)
    dose_unit = models.ForeignKey(DoseUnitCategory, db_column='dose_unit_uuid', null=True, blank=True)
    interval_unit = models.ForeignKey(IntervalUnitCategory, db_column='interval_unit_uuid', null=True, blank=True)

    end_date = models.DateField(blank=True, null=True)

    comment = models.CharField(max_length=255, blank=True, null=True)

    encounter = models.ForeignKey(Encounter, db_column = "encounter_uuid")