# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2019-05-11 02:42
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tecnico', '0051_auto_20190510_2237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='docs_legal',
            name='fecha',
            field=models.DateField(default=datetime.date(2019, 5, 10)),
        ),
        migrations.AlterField(
            model_name='informe',
            name='fecha',
            field=models.DateField(default=datetime.date(2019, 5, 10)),
        ),
    ]