# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-12-21 14:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tecnico', '0005_auto_20181220_0930'),
    ]

    operations = [
        migrations.AddField(
            model_name='operario_nuevo',
            name='vigente',
            field=models.BooleanField(default=True),
        ),
    ]
