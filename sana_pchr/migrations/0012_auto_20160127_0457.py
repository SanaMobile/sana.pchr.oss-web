# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sana_pchr', '0011_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='physician',
            name='recovery_answer',
            field=models.CharField(max_length=45, default='sanapchr'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='physician',
            name='recovery_question',
            field=models.CharField(max_length=45, default='Default password:'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='testcategory',
            name='resultMax',
            field=models.FloatField(default=1000),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='testcategory',
            name='resultMin',
            field=models.FloatField(default=0),
            preserve_default=True,
        ),
    ]
