# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import
from django.db.models import Q

from django.db import models
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

#Importando la tabla de Usuarios de django
from django.contrib.auth.models import User

from apps.operario.models import Razon_Social, Requisitos_RS
import datetime
from django.utils.timezone import now
from datetime import datetime ,date, timedelta

class Operador_Nuevo(models.Model):
    razon_social = models.ForeignKey(Razon_Social, null=True, blank=True, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=150, null= True, blank= True)
    numero_registro = models.IntegerField(null=True, blank=True)
    tipo = models.CharField(max_length=12, null=True, blank=True)
    modalidad = models.CharField(max_length=100, null=True, blank=True)
    domicilio = models.CharField(max_length=200, null=True, blank=True)
    nit = models.CharField(max_length=12, null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    documento_legal = models.TextField(null=True, blank=True)
    digital = models.FileField(upload_to = 'legal', null=True, blank=True)
    # campos para control del operador
    vigente = models.BooleanField(default=True) # indica si se otorgo la devolucion por falta de requisitos
    es_nuevo = models.BooleanField(default=True)
    # renovando = models.BooleanField(default=False)
    en_tramite = models.BooleanField(default=True)

    checklist = models.ManyToManyField(Requisitos_RS, through = 'Checklist_Operario', related_name = 'operario')

    class Meta:
        permissions=(
            ('administrar_operador', 'Puede administrar al operador'),
            ('verificar', 'Puede verificar'),
            ('administrador', 'Puede administrar todo'),
        )

    def __unicode__(self):
        return '{}'.format(self.nombre)

    def tienechecklist(self):
        if Checklist_Operario.objects.filter(operador_nuevo=self).exists():
            return True
        return False
    
    def checklistRenovacion(self):
        pass

    def getnotas(self):
        notas = Nota.objects.filter(operador_n=self).order_by('id').last()
        return  notas

    def notaFenecio(self):
        nota = Nota.objects.filter(operador_n= self, fenecio= False).order_by('id').last()
        return nota

    def tieneobservacion(self):
        if Checklist_Operario.objects.filter(operador_nuevo=self, cumple=False).exists() and self.vigente == True and Vehiculo_Nuevo.objects.filter(operador=self).exists():
            return True
        return False

    def tienevehiculos(self):
        if self.vigente == True:
            if Vehiculo_Nuevo.objects.filter(operador=self).exists():
                return True
            return False
        return False

    def tienevehiobs(self):
        if self.vigente == True:
            vehiculo = Vehiculo_Nuevo.objects.filter(operador=self)
        else:
            vehiculo = []
        if vehiculo != []:
            if Checklist_Vehiculo.objects.filter(vehiculo_nuevo__in=vehiculo, cumple= False).exists():
                return True
            return False
        return False

    def tienevehiobsRenovacion(self):
        if self.vigente == True:
            vehiculo = Vehiculo_Nuevo.objects.filter(operador=self, renovando=True)
        else:
            vehiculo = []
        if vehiculo != []:
            if Checklist_Vehiculo.objects.filter(vehiculo_nuevo__in=vehiculo, vigente=True , cumple= False).exists():
                return True
            return False
        else:
            return False
    
    def estaobservado(self):
        if Informe.objects.filter(operador=self, tipo="OBSERVACION", vigente=True).exists() :
            return True
        return False

    def sedevolvio(self):
        if Informe.objects.filter(operador=self, tipo="DEVOLUCION", vigente=True).exists() :
            return True
        return False
    
    def tieneinformetecnico(self):
        if Informe.objects.filter(operador=self, tipo="INFORME_TECNICO", vigente=True).exists() :
            return True
        return False

    def tieneInformeTecnico(self):
        if Informe.objects.filter(operador=self, tipo="INFORME_TECNICO", vigente=True).exists() :
            return True
        return False

    def tienenota(self):
        if self.vigente == True:
            if Nota.objects.filter(operador_n=self).exists():
                return True
            return False
        return False
    
    def tiene_inf_legal(self):
        if Docs_Legal.objects.filter(operador=self, tipo='INFORME_LEGAL', vigente=True).exists():
            return True
        return False
    
    def tiene_res_administrativa(self):
        if Docs_Legal.objects.filter(operador=self, tipo='RESOLUCION_ADMINISTRATIVA', vigente=True).exists():
            return True
        return False

    def cincodiasplazo(self):
        dias = timedelta(days=6)
        hoy = datetime.now().date()
        if Informe.objects.filter(operador=self, tipo="OBSERVACION", vigente=True).exists():
            devols = Informe.objects.filter(operador=self, tipo="OBSERVACION", vigente=True)
            if len(devols) == 1:
                fecha_informe = devols[0].fecha
                d = probarcincodias = hoy - fecha_informe
                if d >= dias:
                    return True
        return False

class Checklist_Operario(models.Model):
    requisitos = models.ForeignKey(Requisitos_RS, null=True, blank=True, on_delete=models.CASCADE, related_name = 'checklist')
    operador_nuevo = models.ForeignKey(Operador_Nuevo, null=True, blank=True, on_delete=models.CASCADE, related_name = 'checklist_operario')
    observacion = models.TextField(null= True, blank= True)
    cumple = models.BooleanField(default=True)

# modelos para registrar un vehiculo nuevo o de renovacion
class Requisitos_Vehi(models.Model):
    descripcion = models.TextField(null= True, blank= True)
    
    def __unicode__(self):
        # return '{}'.format(self.descripcion)
        return str(self.descripcion)

class Tipo_Vehiculo(models.Model):
    nombre = models.CharField(max_length=50, null=True, blank=True)
    requisitos_v = models.ManyToManyField(Requisitos_Vehi)

    def __unicode__(self):
        return '{}'.format(self.nombre)

class requisitos_vehiculo_tipo(models.Model):
    requisitos_vehi = models.ForeignKey(Requisitos_Vehi, null=True, blank=True, on_delete=models.CASCADE)
    tipo_vehiculo = models.ForeignKey(Tipo_Vehiculo, null=True, blank=True, on_delete=models.CASCADE)
    
    class Meta:
        managed = False
        db_table = 'tecnico_tipo_vehiculo_requisitos_v'

class Vehiculo_Nuevo(models.Model):
    operador = models.ForeignKey(Operador_Nuevo, null=True, blank=True, on_delete=models.CASCADE, related_name='vehiculo')
    tipo = models.ForeignKey(Tipo_Vehiculo, null=True, blank=True, on_delete=models.CASCADE)
    propietario = models.CharField(max_length= 75, null= True, blank= True)
    placa = models.CharField(max_length= 10, null= True, blank= True)
    tipo_vehiculo = models.CharField(max_length= 75, null= True, blank= True)
    marca = models.CharField(max_length= 75, null= True, blank= True)
    modelo = models.IntegerField(null= True, blank= True)
    chasis = models.CharField(max_length= 75, null= True, blank= True)
    capacidad = models.CharField(max_length= 75, null= True, blank= True)
    color = models.CharField(max_length= 50, null= True, blank= True)
    # Variables de control
    es_nuevo = models.BooleanField(default=True)
    renovando = models.BooleanField(default=False) #Muestra si el vehiculo esta renovando tarjeta
    dar_baja = models.BooleanField(default=False) # Variable para que el vehiculo pueda dar de baja en un operador, y se registre en otro operador

    checklist = models.ManyToManyField(Requisitos_Vehi, through = 'Checklist_Vehiculo', related_name = 'vehiculo')
    class Meta:
        permissions=(
            ('emitir_infraccion', 'Puede emitir infraccion'),
        )
    def __unicode__(self):
        return '{}'.format(self.placa)

    def tienecheck(self):
        if Checklist_Vehiculo.objects.filter(vehiculo_nuevo=self).exists():
            return True
        return False
    def tienecheckRenovacion(self):
        if Checklist_Vehiculo.objects.filter(vehiculo_nuevo=self, vigente=True).exists():
            return True
        return False

class Checklist_Vehiculo(models.Model):
    requisitos = models.ForeignKey(Requisitos_Vehi, null=True, blank=True, on_delete=models.CASCADE, related_name = 'checklist')
    vehiculo_nuevo = models.ForeignKey(Vehiculo_Nuevo, null=True, blank=True, on_delete=models.CASCADE, related_name = 'checklist_vehiculo')
    observacion = models.TextField(null= True, blank= True)
    cumple = models.BooleanField(default=True)
    # Variables de control del checklist
    vigente = models.BooleanField(default=True) # variable para saber si el check pertenece a una verificacion actual

class Fotos_Vehiculo(models.Model):
    vehiculo = models.ForeignKey(Vehiculo_Nuevo, null=True, blank=True, on_delete=models.CASCADE, related_name='fotos')
    foto = models.FileField(upload_to = 'fotos-vehiculos', null=True, blank=True)
# Modelo de notas
class Nota(models.Model):
    operador_n =  models.ForeignKey(Operador_Nuevo, null=True, blank=True, on_delete=models.CASCADE)
    cite = models.CharField(max_length= 10, null= True, blank= True)
    fecha = models.DateField(null=True, blank=True)
    nombre_ente = models.CharField(max_length= 100, null= True, blank= True)
    representante_ente = models.CharField(max_length= 100, null= True, blank= True)
    cargo_repr = models.CharField(max_length= 100, null= True, blank= True)
    ruta_solicitada = models.TextField(null= True, blank= True)
    cantidad_tarjetas = models.IntegerField(null= True, blank= True)
    devuelto = models.BooleanField(default=False) # indica si se otorgo la devolucion por falta de requisitos
    # Variables de control
    fenecio = models.BooleanField(default=False) # control para saber si la nota de un operador ya feneció, ejm. si se quiere hacer renovacion se necesita que la nota anterior ya fenezca.
# modelo Informes observados devolucion info técnico
class Informe(models.Model):
    operador =  models.ForeignKey(Operador_Nuevo, null=True, blank=True, on_delete=models.CASCADE)
    cite = models.CharField(max_length= 10, null= True, blank= True)
    fecha = models.DateField(null=True, blank=True)
    tipo = models.CharField(max_length= 20, null= True, blank= True)
    ans_tecnico = models.TextField(null= True, blank=True)
    concluciones = models.TextField(null= True, blank=True)
    anterior = models.ForeignKey("Informe", null=True, blank=True, on_delete=models.CASCADE)
    #variables de control
    vigente = models.BooleanField(default=True)

class Docs_Legal(models.Model):
    operador =  models.ForeignKey(Operador_Nuevo, null=True, blank=True, on_delete=models.CASCADE)
    tipo = models.CharField(max_length= 30, null= True, blank= True)
    descripcion = RichTextUploadingField(null= True, blank= True)
    cite = models.CharField(max_length= 10, null= True, blank= True)
    fecha = models.DateField(null=True, blank=True)
    numero_ra = models.IntegerField(null= True, blank= True)
    #variables de control
    vigente = models.BooleanField(default=True)
    class Meta:
        permissions=(
            ('administrar_doc_legal', 'Puede administrar documentos legales'),
        )

class Ruta(models.Model):
    operador =  models.ForeignKey(Operador_Nuevo, null=True, blank=True, on_delete=models.CASCADE)
    ruta = models.CharField(max_length= 100, null= True, blank= True)
    hora = models.CharField(max_length= 100, null= True, blank= True)

class Infraccion(models.Model):
    vehiculo = models.ForeignKey(Vehiculo_Nuevo, null=True, blank=True, on_delete=models.CASCADE)
    lugar = models.CharField(max_length=250, null=True, blank=True)
    tipo = models.TextField(null=True, blank=True)
    observacion = models.TextField(null=True, blank=True)
    licencia = models.CharField(max_length=15, null=True, blank=True)
    fecha = models.DateField(null=True, blank=True)

    cancelado = models.BooleanField(default=False)