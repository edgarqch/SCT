# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2019-03-18 21:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tecnico', '0029_nota_devuelto'),
    ]

    operations = [
        migrations.AddField(
            model_name='operador_nuevo',
            name='renovando',
            field=models.BooleanField(default=False),
        ),
    ]
