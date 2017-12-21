# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sana_pchr', '0009_manual'),
    ]

    operations = [
        migrations.AddField(
            model_name='clinic',
            name='language',
            field=models.CharField(max_length=2, default='ar'),
            preserve_default=True,
        ),
    ]
