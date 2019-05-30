# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2019-02-11 21:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tecnico', '0020_auto_20190130_1106'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehiculo_nuevo',
            name='capasidad',
            field=models.CharField(blank=True, max_length=75, null=True),
        ),
        migrations.AddField(
            model_name='vehiculo_nuevo',
            name='chasis',
            field=models.CharField(blank=True, max_length=75, null=True),
        ),
        migrations.AddField(
            model_name='vehiculo_nuevo',
            name='color',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='vehiculo_nuevo',
            name='marca',
            field=models.CharField(blank=True, max_length=75, null=True),
        ),
        migrations.AddField(
            model_name='vehiculo_nuevo',
            name='modelo',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vehiculo_nuevo',
            name='tipo_vehiculo',
            field=models.CharField(blank=True, max_length=75, null=True),
        ),
    ]
