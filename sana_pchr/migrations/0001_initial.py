# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from sana_pchr.models.fields import *
from sana_pchr.crypto import Credential

class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Clinic',
            fields=[
                ('uuid', UUIDField(primary_key=True, max_length=36, serialize=False, default=DefaultFuncs.make_uuid)),
                ('created', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('updated', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('synchronized', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('name', models.CharField(max_length=45)),
                ('longitude', models.FloatField(null=True, blank=True)),
                ('latitude', models.FloatField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Clinic_Physician',
            fields=[
                ('uuid', UUIDField(primary_key=True, max_length=36, serialize=False, default=DefaultFuncs.make_uuid)),
                ('created', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('updated', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('synchronized', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('clinic', models.ForeignKey(db_column='clinic_uuid', to='sana_pchr.Clinic')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('uuid', UUIDField(primary_key=True, max_length=36, serialize=False, default=DefaultFuncs.make_uuid)),
                ('created', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('updated', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('synchronized', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('name', models.CharField(max_length=45)),
                ('deviceMAC', models.CharField(max_length=17)),
                ('key', CredentialField(default=Credential.generate, editable=False)),
                ('token', models.CharField(max_length=32, default=DefaultFuncs.make_uuid)),
                ('clinic', models.ForeignKey(db_column='clinic_uuid', blank=True, null=True, to='sana_pchr.Clinic')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Encounter',
            fields=[
                ('uuid', UUIDField(primary_key=True, max_length=36, serialize=False, default=DefaultFuncs.make_uuid)),
                ('created', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('updated', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('synchronized', models.DateTimeField(default=DefaultFuncs.getNow)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EncounterCategory',
            fields=[
                ('uuid', UUIDField(primary_key=True, max_length=36, serialize=False, default=DefaultFuncs.make_uuid)),
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
            name='Patient',
            fields=[
                ('uuid', UUIDField(primary_key=True, max_length=36, serialize=False, default=DefaultFuncs.make_uuid)),
                ('created', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('updated', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('synchronized', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('firstName', models.CharField(max_length=45)),
                ('lastName', models.CharField(blank=True, max_length=45)),
                ('UNHCR', models.CharField(blank=True, max_length=45)),
                ('birthYear', models.CharField(blank=True, max_length=45)),
                ('birthCity', models.CharField(blank=True, max_length=45)),
                ('picture', models.ImageField(upload_to='', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Patient_Physician',
            fields=[
                ('uuid', UUIDField(primary_key=True, max_length=36, serialize=False, default=DefaultFuncs.make_uuid)),
                ('created', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('updated', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('synchronized', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('patient', models.ForeignKey(db_column='patient_uuid', to='sana_pchr.Patient')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Physician',
            fields=[
                ('uuid', UUIDField(primary_key=True, max_length=36, serialize=False, default=DefaultFuncs.make_uuid)),
                ('created', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('updated', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('synchronized', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('firstName', models.CharField(max_length=45)),
                ('lastName', models.CharField(max_length=45)),
                ('picture', models.ImageField(upload_to='', blank=True)),
                ('hashedPIN', models.CharField(max_length=128)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('phone', models.CharField(blank=True, max_length=45)),
                ('recovery_question', models.CharField(blank=True, max_length=45)),
                ('recovery_answer', models.CharField(blank=True, max_length=45)),
                ('recovery_key', DerivedCredentialField(null=True, blank=True, editable=False, max_length=128)),
                ('key', CredentialField(default=Credential.generate, editable=False)),
                ('clinics', models.ManyToManyField(to='sana_pchr.Clinic', through='sana_pchr.Clinic_Physician')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('uuid', UUIDField(primary_key=True, max_length=36, serialize=False, default=DefaultFuncs.make_uuid)),
                ('created', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('updated', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('synchronized', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('value', models.CharField(max_length=45)),
                ('comment', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RecordCategory',
            fields=[
                ('uuid', UUIDField(primary_key=True, max_length=36, serialize=False, default=DefaultFuncs.make_uuid)),
                ('created', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('updated', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('synchronized', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('displayName', models.CharField(max_length=45)),
                ('recordType', models.IntegerField()),
                ('resultDataType', models.CharField(blank=True, max_length=45)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('uuid', UUIDField(primary_key=True, max_length=36, serialize=False, default=DefaultFuncs.make_uuid)),
                ('created', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('updated', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('synchronized', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('result', models.CharField(max_length=45)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TestCategory',
            fields=[
                ('uuid', UUIDField(primary_key=True, max_length=36, serialize=False, default=DefaultFuncs.make_uuid)),
                ('created', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('updated', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('synchronized', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('displayName', models.CharField(max_length=45)),
                ('resultType', models.IntegerField()),
                ('resultMin', models.FloatField(blank=True, null=True)),
                ('resultMax', models.FloatField(blank=True, null=True)),
                ('resultUnits', models.CharField(blank=True, max_length=45)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Visit',
            fields=[
                ('uuid', UUIDField(primary_key=True, max_length=36, serialize=False, default=DefaultFuncs.make_uuid)),
                ('created', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('updated', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('synchronized', models.DateTimeField(default=DefaultFuncs.getNow)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VisitCategory',
            fields=[
                ('uuid', UUIDField(primary_key=True, max_length=36, serialize=False, default=DefaultFuncs.make_uuid)),
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
        migrations.AddField(
            model_name='visit',
            name='category',
            field=models.ForeignKey(db_column='category_uuid', to='sana_pchr.VisitCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='visit',
            name='patient',
            field=models.ForeignKey(db_column='patient_uuid', to='sana_pchr.Patient'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='test',
            name='category',
            field=models.ForeignKey(db_column='category_uuid', to='sana_pchr.TestCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='test',
            name='encounter',
            field=models.ForeignKey(db_column='encounter_uuid', to='sana_pchr.Encounter'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='record',
            name='category',
            field=models.ForeignKey(db_column='category_uuid', to='sana_pchr.RecordCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='record',
            name='encounter',
            field=models.ForeignKey(db_column='encounter_uuid', to='sana_pchr.Encounter'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='patient_physician',
            name='physician',
            field=models.ForeignKey(db_column='physician_uuid', to='sana_pchr.Physician'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='patient',
            name='physicians',
            field=models.ManyToManyField(to='sana_pchr.Physician', through='sana_pchr.Patient_Physician'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='encounter',
            name='category',
            field=models.ForeignKey(db_column='category_uuid', to='sana_pchr.EncounterCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='encounter',
            name='clinic',
            field=models.ForeignKey(db_column='clinic_uuid', to='sana_pchr.Clinic'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='encounter',
            name='device',
            field=models.ForeignKey(db_column='device_uuid', to='sana_pchr.Device'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='encounter',
            name='physician',
            field=models.ForeignKey(db_column='physician_uuid', to='sana_pchr.Physician'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='encounter',
            name='visit',
            field=models.ForeignKey(db_column='visit_uuid', to='sana_pchr.Visit'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='clinic_physician',
            name='physician',
            field=models.ForeignKey(db_column='physician_uuid', to='sana_pchr.Physician'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='clinic',
            name='physicians',
            field=models.ManyToManyField(to='sana_pchr.Physician', blank=True, through='sana_pchr.Clinic_Physician'),
            preserve_default=True,
        ),
    ]
