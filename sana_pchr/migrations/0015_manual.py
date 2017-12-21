# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from sana_pchr.models.base import CategoryModel;
from sana_pchr.models import TestCategory
import uuid

from django.db import migrations

'''
    The purpose of this migration is to initially populate  the fields of the
    arabic fields with their english counterparts
'''

def forwards_func(apps, schema_editor):
    db_alias = schema_editor.connection.alias

    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version

    categories = [x.__name__ for x in CategoryModel.__subclasses__()]

    MedicationCategory = apps.get_model("sana_pchr", "MedicationCategory")
    mcs = MedicationCategory.objects.using(db_alias).all()

    for mc in mcs:
        if mc.displayName.__len__() < 6:
            mc.abbrev = mc.displayName
        else:
            mc.abbrev = mc.displayName[0:6]
        mc.save()

def reverse_func(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('sana_pchr', '0014_medicationcategory_abbrev'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_code=reverse_func)
    ]
