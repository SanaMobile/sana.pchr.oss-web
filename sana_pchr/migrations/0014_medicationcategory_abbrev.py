# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sana_pchr', '0013_auto_20160129_2251'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicationcategory',
            name='abbrev',
            field=models.CharField(blank=True, max_length=10),
            preserve_default=True,
        ),
    ]
