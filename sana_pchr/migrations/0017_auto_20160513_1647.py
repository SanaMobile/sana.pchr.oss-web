# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sana_pchr', '0016_auto_20160202_0532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='app',
            name='checksum',
            field=models.CharField(max_length=64, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='app',
            name='pkg',
            field=models.FileField(blank=True, upload_to='app/'),
            preserve_default=True,
        ),
    ]
