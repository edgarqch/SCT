# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2019-07-25 03:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tramite', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tramite',
            name='finalizado',
            field=models.BooleanField(default=False),
        ),
    ]
