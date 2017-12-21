# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sana_pchr', '0004_auto_20160107_0813'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='UNHCR',
            field=models.CharField(max_length=45, db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='patient',
            name='birthCity',
            field=models.CharField(max_length=45, db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='patient',
            name='birthYear',
            field=models.CharField(max_length=45, db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='patient',
            name='firstName',
            field=models.CharField(max_length=45, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='patient',
            name='lastName',
            field=models.CharField(max_length=45, db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='physician',
            name='email',
            field=models.EmailField(max_length=254, db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='physician',
            name='phone',
            field=models.CharField(max_length=45, db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='medicationcategory',
            name='otherName',
            field=models.CharField(null=True, max_length=256, blank=True),
            preserve_default=True,
        )
    ]
