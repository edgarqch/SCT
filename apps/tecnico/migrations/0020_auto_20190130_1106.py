# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2019-01-30 15:06
from __future__ import unicode_literals

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tecnico', '0019_auto_20190130_0929'),
    ]

    operations = [
        migrations.AlterField(
            model_name='docs_legal',
            name='descripcion',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True),
        ),
    ]