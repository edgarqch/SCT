# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2019-02-05 20:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operario', '0003_requisitos_razon_social'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='operario',
            name='razon_social',
        ),
        migrations.RemoveField(
            model_name='rep_legal',
            name='operario',
        ),
        migrations.DeleteModel(
            name='Operario',
        ),
        migrations.DeleteModel(
            name='Rep_Legal',
        ),
    ]