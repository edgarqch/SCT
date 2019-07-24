# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import

from django.contrib import admin

from apps.tecnico.models import Operador_Nuevo, Requisitos_Vehi, Tipo_Vehiculo, Docs_Legal, Marca, Checklist_Operario,\
Vehiculo_Nuevo, Checklist_Vehiculo, Fotos_Vehiculo, Nota, Informe, Ruta, Infraccion, requisitos_vehiculo_tipo

admin.site.register(Operador_Nuevo)
admin.site.register(Requisitos_Vehi)
admin.site.register(Tipo_Vehiculo)
admin.site.register(Docs_Legal)
admin.site.register(Marca)
admin.site.register(Checklist_Operario)
admin.site.register(Vehiculo_Nuevo)
admin.site.register(Checklist_Vehiculo)
admin.site.register(Fotos_Vehiculo)
admin.site.register(Nota)
admin.site.register(Informe)
admin.site.register(Ruta)
admin.site.register(Infraccion)
admin.site.register(requisitos_vehiculo_tipo)
# Register your models here.
