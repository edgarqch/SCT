# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2019-05-11 02:35
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tecnico', '0049_auto_20190510_1753'),
    ]

    operations = [
        migrations.AlterField(
            model_name='docs_legal',
            name='fecha',
            field=models.DateField(default=datetime.datetime.now),
        ),
    ]
