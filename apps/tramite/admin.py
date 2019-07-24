# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import

from django.contrib import admin

from apps.tramite.models import Tramite, Asignar_Vehiculo

admin.site.register(Tramite)
admin.site.register(Asignar_Vehiculo)
# Register your models here.
