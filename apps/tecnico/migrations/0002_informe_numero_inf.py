# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2019-07-20 14:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tecnico', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='informe',
            name='numero_inf',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]