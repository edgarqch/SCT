# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2019-03-26 19:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tecnico', '0034_vehiculo_nuevo_renovando'),
    ]

    operations = [
        migrations.AddField(
            model_name='checklist_vehiculo',
            name='vigente',
            field=models.BooleanField(default=True),
        ),
    ]
