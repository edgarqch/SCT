# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2019-02-05 20:54
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tramite', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tramite',
            old_name='obserbacion2',
            new_name='baja_observacion',
        ),
        migrations.RenameField(
            model_name='tramite',
            old_name='obserbaciones',
            new_name='observaciones',
        ),
    ]
