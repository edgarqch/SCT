# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2019-05-05 01:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tecnico', '0044_auto_20190504_1646'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='operador_nuevo',
            options={'permissions': (('administrar_operador', 'Puede administrar al operador'),)},
        ),
    ]