# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import

from django.contrib import admin

from apps.tecnico.models import Operador_Nuevo, Requisitos_Vehi, Tipo_Vehiculo, Docs_Legal

admin.site.register(Operador_Nuevo)
admin.site.register(Requisitos_Vehi)
admin.site.register(Tipo_Vehiculo)
admin.site.register(Docs_Legal)
# Register your models here.
