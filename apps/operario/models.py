# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from django.db import models

#Importando la tabla de Usuarios de django
from django.contrib.auth.models import User

class Requisitos_RS (models.Model):
    descripcion = models.TextField(null= True, blank= True)
    
    def __unicode__(self):
        return '{}'.format(self.descripcion)

class Razon_Social(models.Model):
    nombre = models.CharField(max_length=50, null=True, blank=True)
    requisitos = models.ManyToManyField(Requisitos_RS, related_name= 'razon_social_requisitos')

    def __unicode__(self):
        return '{}'.format(self.nombre)

class requisitos_razon_social(models.Model):
    requisitos_rs = models.ForeignKey(Requisitos_RS, null=True, blank=True, on_delete=models.CASCADE)
    razon_social = models.ForeignKey(Razon_Social, null=True, blank=True, on_delete=models.CASCADE)
    
    def __unicode__(self):
        return '{} / {}'.format(self.razon_social, self.requisitos_rs)

    class Meta:
        managed = False
        db_table = 'operario_razon_social_requisitos'


# class Rep_Legal (models.Model):
#     operario = models.ForeignKey(Operador, null=True, blank=True, on_delete=models.CASCADE)
#     ci = models.CharField(max_length=100, null=True, blank=True)
#     nombre_r = models.CharField(max_length=100, null=True, blank=True)
#     domicilio_r = models.CharField(max_length=100, null=True, blank=True)
#     estado_activo = models.BooleanField(default=False)