# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2019-01-23 19:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tecnico', '0015_informe'),
    ]

    operations = [
        migrations.AlterField(
            model_name='informe',
            name='fecha',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='nota',
            name='fecha',
            field=models.DateField(blank=True, null=True),
        ),
    ]