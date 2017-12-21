# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from sana_pchr.models.fields import DefaultFuncs
from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('sana_pchr', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
                model_name='device',
                name='lastSynchronized',
                field=models.DateTimeField(default=DefaultFuncs.getNow),
                preserve_default=True,
        ),
        migrations.AddField(
                model_name='clinic',
                name='deleted',
                field=models.DateTimeField(default=DefaultFuncs.far_future()),
                preserve_default=True,
        ),
        migrations.AddField(
                model_name='clinic_physician',
                name='deleted',
                field=models.DateTimeField(default=DefaultFuncs.far_future()),
                preserve_default=True,
        ),
        migrations.AddField(
                model_name='device',
                name='deleted',
                field=models.DateTimeField(default=DefaultFuncs.far_future()),
                preserve_default=True,
        ),
        migrations.AddField(
                model_name='encounter',
                name='deleted',
                field=models.DateTimeField(default=DefaultFuncs.far_future()),
                preserve_default=True,
        ),
        migrations.AddField(
                model_name='encountercategory',
                name='deleted',
                field=models.DateTimeField(default=DefaultFuncs.far_future()),
                preserve_default=True,
        ),
        migrations.AddField(
                model_name='patient',
                name='deleted',
                field=models.DateTimeField(default=DefaultFuncs.far_future()),
                preserve_default=True,
        ),
        migrations.AddField(
                model_name='patient_physician',
                name='deleted',
                field=models.DateTimeField(default=DefaultFuncs.far_future()),
                preserve_default=True,
        ),
        migrations.AddField(
                model_name='physician',
                name='deleted',
                field=models.DateTimeField(default=DefaultFuncs.far_future()),
                preserve_default=True,
        ),
        migrations.AddField(
                model_name='record',
                name='deleted',
                field=models.DateTimeField(default=DefaultFuncs.far_future()),
                preserve_default=True,
        ),
        migrations.AddField(
                model_name='recordcategory',
                name='deleted',
                field=models.DateTimeField(default=DefaultFuncs.far_future()),
                preserve_default=True,
        ),
        migrations.AddField(
                model_name='test',
                name='deleted',
                field=models.DateTimeField(default=DefaultFuncs.far_future()),
                preserve_default=True,
        ),
        migrations.AddField(
                model_name='testcategory',
                name='deleted',
                field=models.DateTimeField(default=DefaultFuncs.far_future()),
                preserve_default=True,
        ),
        migrations.AddField(
                model_name='visit',
                name='deleted',
                field=models.DateTimeField(default=DefaultFuncs.far_future()),
                preserve_default=True,
        ),
        migrations.AddField(
                model_name='visitcategory',
                name='deleted',
                field=models.DateTimeField(default=DefaultFuncs.far_future()),
                preserve_default=True,
        ),
        migrations.AlterField(
            model_name='patient_physician',
            name='uuid',
            field=models.CharField(primary_key=True, max_length=36, serialize=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='clinic_physician',
            name='uuid',
            field=models.CharField(primary_key=True, max_length=36, serialize=False),
            preserve_default=True,
        ),
    ]
