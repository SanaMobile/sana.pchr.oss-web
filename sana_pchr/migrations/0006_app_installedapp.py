# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sana_pchr', '0005_auto_20160110_0006'),
    ]

    operations = [
        migrations.CreateModel(
            name='App',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('version', models.PositiveIntegerField()),
                ('pkg', models.FileField(upload_to='app/')),
                ('checksum', models.CharField(max_length=64)),
            ],
            options={
                'ordering': ['-version'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InstalledApp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('version', models.PositiveIntegerField()),
                ('device', models.ForeignKey(to='sana_pchr.Device', db_column='device_uuid')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
