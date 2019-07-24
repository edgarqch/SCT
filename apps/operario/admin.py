# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import

from django.contrib import admin

from apps.operario.models import Razon_Social, Requisitos_RS, requisitos_razon_social

# admin.site.register(Operario)
admin.site.register(requisitos_razon_social)
admin.site.register(Razon_Social)
admin.site.register(Requisitos_RS)

# Register your models here.
