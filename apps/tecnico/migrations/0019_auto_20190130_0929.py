# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2019-01-30 13:29
from __future__ import unicode_literals

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tecnico', '0018_auto_20190129_2256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='docs_legal',
            name='descripcion',
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
    ]
