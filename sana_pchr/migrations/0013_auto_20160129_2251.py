# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sana_pchr', '0012_auto_20160127_0457'),
    ]

    operations = [
        migrations.AddField(
            model_name='doseunitcategory',
            name='priority',
            field=models.IntegerField(default=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='encountercategory',
            name='priority',
            field=models.IntegerField(default=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='intervalunitcategory',
            name='priority',
            field=models.IntegerField(default=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='medicationcategory',
            name='priority',
            field=models.IntegerField(default=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='medicationgroupcategory',
            name='priority',
            field=models.IntegerField(default=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recordcategory',
            name='priority',
            field=models.IntegerField(default=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='visitcategory',
            name='priority',
            field=models.IntegerField(default=1),
            preserve_default=True,
        ),
    ]
