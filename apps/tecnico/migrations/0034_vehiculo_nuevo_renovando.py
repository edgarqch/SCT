# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2019-03-25 14:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tecnico', '0033_nota_fenecio'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehiculo_nuevo',
            name='renovando',
            field=models.BooleanField(default=False),
        ),
    ]