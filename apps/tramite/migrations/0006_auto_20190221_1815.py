# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2019-02-21 22:15
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tramite', '0005_auto_20190221_1815'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tramite',
            old_name='checklist',
            new_name='asignar_v',
        ),
    ]
