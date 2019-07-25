# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from django.db import models

#Importando la tabla de Usuarios de django
from django.contrib.auth.models import User

from apps.tecnico.models import Operador_Nuevo, Vehiculo_Nuevo

class Tramite(models.Model):
    tipo_tramite = models.CharField(max_length=50, null=True, blank=True, default="EXTENSION TARJETA DE OPERACION INTERPROVINCIAL")
    solicitante = models.ForeignKey(Operador_Nuevo, null=True, blank=True, on_delete=models.CASCADE)
    fecha_ingreso = models.DateField(null=True, blank=True)
    hora_ingreso = models.TimeField(null=True, blank=True)
    num_fojas = models.IntegerField(null=True, blank=True)
    estado = models.CharField(max_length=10, null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True, default="EXTENSION DE TARJETAS DE OPERACIONES")
    baja_observacion = models.TextField(null=True, blank=True)

    tiene_orden = models.BooleanField(default=False)
    finalizar = models.BooleanField(default=False)
    finalizado = models.BooleanField(default=False)
    vigente = models.BooleanField(default=True) # Para saber cual fue el ultimo tramite que realizó el operador

    asignar_v = models.ManyToManyField(Vehiculo_Nuevo, through = 'Asignar_Vehiculo', related_name = 'tramite')
    class Meta:
        permissions=(
            ('administrar_tramite', 'Puede administrar tramites'),
        )

    def __unicode__(self):
        return '{} / {}'.format(self.solicitante, self.fecha_ingreso)

class Asignar_Vehiculo(models.Model):
    tramite = models.ForeignKey(Tramite, null=True, blank=True, on_delete=models.CASCADE, related_name = 'asignar')
    vehiculo = models.ForeignKey(Vehiculo_Nuevo, null=True, blank=True, on_delete=models.CASCADE, related_name = 'asig_vehiculo')
    validez = models.IntegerField(null=True, blank=True, default=1)
    gestion = models.IntegerField(null=True, blank=True)
    monto = models.IntegerField(null=True, blank=True)
    valida_del = models.DateField(null=True, blank=True)
    valida_al = models.DateField(null=True, blank=True)
    # variables de control
    tiene_tarjeta = models.BooleanField(default=False)  #para saber si la tarjeta fue impresa
    caducado = models.BooleanField(default=False) #para saber si la tarjeta caducó luego del año de validez
    
    def __unicode__(self):
        return '{} / {} / {}'.format(self.tramite, self.vehiculo, self.gestion)