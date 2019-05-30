# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2019-02-17 21:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tecnico', '0024_ruta'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ruta',
            old_name='hora',
            new_name='hora_i',
        ),
        migrations.RenameField(
            model_name='ruta',
            old_name='ruta',
            new_name='hora_v',
        ),
        migrations.AddField(
            model_name='ruta',
            name='ruta_i',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='ruta',
            name='ruta_v',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
