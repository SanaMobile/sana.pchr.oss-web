# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sana_pchr', '0007_patient_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='doseunitcategory',
            name='displayNameAr',
            field=models.CharField(default='', max_length=127),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='encountercategory',
            name='displayNameAr',
            field=models.CharField(default='', max_length=127),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='intervalunitcategory',
            name='displayNameAr',
            field=models.CharField(default='', max_length=127),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='medication',
            name='comment',
            field=models.CharField(blank=True, max_length=255, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='medicationcategory',
            name='displayNameAr',
            field=models.CharField(default='', max_length=127),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='medicationcategory',
            name='interaction_warning',
            field=models.CharField(blank=True, max_length=255, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='medicationgroupcategory',
            name='displayNameAr',
            field=models.CharField(default='', max_length=127),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='patient',
            name='phone',
            field=models.CharField(blank=True, db_index=True, max_length=25),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='patient',
            name='provider_id',
            field=models.CharField(blank=True, db_index=True, max_length=45),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='physician',
            name='type',
            field=models.CharField(default='D', max_length=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recordcategory',
            name='displayNameAr',
            field=models.CharField(default='', max_length=127),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='testcategory',
            name='displayNameAr',
            field=models.CharField(default='', max_length=127),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='testcategory',
            name='resultUnitsAr',
            field=models.CharField(blank=True, max_length=127, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='visitcategory',
            name='displayNameAr',
            field=models.CharField(default='', max_length=127),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='doseunitcategory',
            name='displayName',
            field=models.CharField(max_length=127),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='encountercategory',
            name='displayName',
            field=models.CharField(max_length=127),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intervalunitcategory',
            name='displayName',
            field=models.CharField(max_length=127),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='medicationcategory',
            name='displayName',
            field=models.CharField(max_length=127),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='medicationgroupcategory',
            name='displayName',
            field=models.CharField(max_length=127),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='record',
            name='value',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='recordcategory',
            name='displayName',
            field=models.CharField(max_length=127),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='test',
            name='result',
            field=models.CharField(max_length=1023),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='testcategory',
            name='displayName',
            field=models.CharField(max_length=127),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='testcategory',
            name='resultUnits',
            field=models.CharField(blank=True, max_length=127, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='visitcategory',
            name='displayName',
            field=models.CharField(max_length=127),
            preserve_default=True,
        ),
    ]
