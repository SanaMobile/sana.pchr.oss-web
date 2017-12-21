# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime
from sana_pchr.models.fields import UUIDField, DefaultFuncs

class Migration(migrations.Migration):

    dependencies = [
        ('sana_pchr', '0003_manual'),
    ]

    operations = [
        migrations.CreateModel(
            name='DoseUnitCategory',
            fields=[
                ('uuid', UUIDField(default=DefaultFuncs.make_uuid, serialize=False, primary_key=True, max_length=36)),
                ('deleted', models.DateTimeField(default=datetime.datetime(9000, 12, 31, 23, 59, 59, 999999, tzinfo=utc))),
                ('created', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('updated', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('synchronized', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('displayName', models.CharField(max_length=45)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IntervalUnitCategory',
            fields=[
                ('uuid', UUIDField(default=DefaultFuncs.make_uuid, serialize=False, primary_key=True, max_length=36)),
                ('deleted', models.DateTimeField(default=datetime.datetime(9000, 12, 31, 23, 59, 59, 999999, tzinfo=utc))),
                ('created', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('updated', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('synchronized', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('displayName', models.CharField(max_length=45)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MedicationGroupCategory',
            fields=[
                ('uuid', UUIDField(default=DefaultFuncs.make_uuid, serialize=False, primary_key=True, max_length=36)),
                ('deleted', models.DateTimeField(default=datetime.datetime(9000, 12, 31, 23, 59, 59, 999999, tzinfo=utc))),
                ('created', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('updated', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('synchronized', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('displayName', models.CharField(max_length=45)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MedicationCategory',
            fields=[
                ('uuid', UUIDField(default=DefaultFuncs.make_uuid, serialize=False, primary_key=True, max_length=36)),
                ('deleted', models.DateTimeField(default=datetime.datetime(9000, 12, 31, 23, 59, 59, 999999, tzinfo=utc))),
                ('created', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('updated', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('synchronized', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('displayName', models.CharField(max_length=45)),
                ('otherName', models.CharField(null=True, max_length=256)),
                ('group',models.ForeignKey(to='sana_pchr.MedicationGroupCategory', db_column='group_uuid')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Medication',
            fields=[
                ('uuid', UUIDField(default=DefaultFuncs.make_uuid, serialize=False, primary_key=True, max_length=36)),
                ('deleted', models.DateTimeField(default=datetime.datetime(9000, 12, 31, 23, 59, 59, 999999, tzinfo=utc))),
                ('created', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('updated', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('synchronized', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('dose', models.FloatField(null=True, blank=True)),
                ('interval', models.FloatField(null=True, blank=True)),
                ('times', models.IntegerField(null=True, blank=True)),
                ('end_date', models.DateField(null=True, blank=True)),
                ('dose_unit', models.ForeignKey(to='sana_pchr.DoseUnitCategory', db_column='dose_unit_uuid')),
                ('encounter', models.ForeignKey(to='sana_pchr.Encounter', db_column='encounter_uuid')),
                ('interval_unit', models.ForeignKey(to='sana_pchr.IntervalUnitCategory', db_column='interval_unit_uuid')),
                ('category', models.ForeignKey(to='sana_pchr.MedicationCategory', db_column='category_uuid')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='medicationcategory',
            name='dose_default',
            field=models.FloatField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='medicationcategory',
            name='dose_unit',
            field=models.ForeignKey(null=True, blank=True, to='sana_pchr.DoseUnitCategory', db_column='dose_unit_uuid'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='medicationcategory',
            name='interval_default',
            field=models.FloatField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='medicationcategory',
            name='interval_unit',
            field=models.ForeignKey(null=True, blank=True, to='sana_pchr.IntervalUnitCategory', db_column='interval_unit_uuid'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='medicationcategory',
            name='times_default',
            field=models.IntegerField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='medication',
            name='dose_unit',
            field=models.ForeignKey(null=True, blank=True, to='sana_pchr.DoseUnitCategory', db_column='dose_unit_uuid'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='medication',
            name='interval',
            field=models.IntegerField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='medication',
            name='interval_unit',
            field=models.ForeignKey(null=True, blank=True, to='sana_pchr.IntervalUnitCategory', db_column='interval_unit_uuid'),
            preserve_default=True,
        ),
    ]
