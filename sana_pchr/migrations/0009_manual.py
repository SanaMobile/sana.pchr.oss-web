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

    models = [apps.get_model("sana_pchr", x) for x in categories]

    for model in models:
        for object in model.objects.using(db_alias).all():
            object.displayNameAr = object.displayName
            object.save()

    cat = apps.get_model("sana_pchr", "TestCategory")
    for test in cat.objects.using(db_alias).all():
        test.resultUnitsAr = test.resultUnits
        test.save()

class Migration(migrations.Migration):
    dependencies = [
        ('sana_pchr', '0008_auto_20160122_2107'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_code=None)
    ]
