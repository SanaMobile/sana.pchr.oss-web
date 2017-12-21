# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from sana_pchr.models.fields import DefaultFuncs



class Migration(migrations.Migration):

    dependencies = [
        ('sana_pchr', '0015_manual'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='currentVersion',
            field=models.CharField(blank=True, max_length=3),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='device',
            name='lastUpdated',
            field=models.DateField(default=DefaultFuncs.getNow),
            preserve_default=True,
        ),
    ]
