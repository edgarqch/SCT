# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-12-19 22:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('operario', '0001_initial'),
        ('tecnico', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Checklist_Operario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('observacion', models.TextField(blank=True, null=True)),
                ('cumple', models.BooleanField(default=True)),
                ('operario_nuevo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checklist_operario', to='tecnico.Operario_Nuevo')),
                ('requisitos', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checklist', to='operario.Requisitos_RS')),
            ],
        ),
        migrations.CreateModel(
            name='Requisitos_Vehi',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='operario_nuevo',
            name='checklist',
            field=models.ManyToManyField(related_name='operario', through='tecnico.Checklist_Operario', to='operario.Requisitos_RS'),
        ),
    ]
