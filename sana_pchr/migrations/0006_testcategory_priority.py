# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sana_pchr', '0005_auto_20160110_0006'),
    ]

    operations = [
        migrations.AddField(
            model_name='testcategory',
            name='priority',
            field=models.IntegerField(default=1),
            preserve_default=True,
        ),
    ]
