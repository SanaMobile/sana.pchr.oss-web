# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from sana_pchr.models.fields import *
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('sana_pchr', '0017_auto_20160513_1647'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('uuid', UUIDField(serialize=False, default=DefaultFuncs.make_uuid, primary_key=True, max_length=36)),
                ('deleted', models.DateTimeField(default=datetime.datetime(9000, 12, 31, 23, 59, 59, 999999, tzinfo=utc))),
                ('created', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('updated', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('synchronized', models.DateTimeField(default=DefaultFuncs.getNow)),
                ('user', models.CharField(max_length=36)),
                ('device', models.CharField(max_length=36)),
                ('clinic', models.CharField(max_length=36)),
                ('status', models.CharField(max_length=16)),
                ('code', models.CharField(max_length=64)),
                ('message', models.CharField(blank=True, max_length=127)),
                ('exception', models.CharField(blank=True, max_length=127)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
