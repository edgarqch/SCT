from __future__ import absolute_import
from __future__ import unicode_literals
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.http import HttpResponseRedirect 
import json

# Import your forms here.
from apps.tecnico.form import OperarioNuevoForm, VehiculoNForm

# Import your models here.
from apps.tecnico.models import Operador_Nuevo, Vehiculo_Nuevo, Tipo_Vehiculo, Checklist_Operario, Checklist_Vehiculo
from apps.operario.models import Requisitos_RS, requisitos_razon_social

def diaLiteral(dia):
    if dia == '1':
        dia = 'un'
    elif dia == '2':
        dia ='dos'
    elif dia == '3':
        dia = 'tres'
    elif dia == '4':
        dia ='cuatro'
    elif dia == '5':
        dia = 'cinco'
    elif dia == '6':
        dia ='seis'
    elif dia == '7':
        dia = 'siete'
    elif dia == '8':
        dia ='ocho'
    elif dia == '9':
        dia = 'nueve'
    elif dia == '10':
        dia ='diez'
    elif dia == '11':
        dia = 'once'
    elif dia == '12':
        dia ='doce'
    elif dia == '13':
        dia = 'trece'
    elif dia == '14':
        dia ='catorce'
    elif dia == '15':
        dia = 'quince'
    elif dia == '16':
        dia ='dieciseis'
    elif dia == '17':
        dia = 'diecisiete'
    elif dia == '18':
        dia = 'dieciocho'
    elif dia == '19':
        dia ='diecinueve'
    elif dia == '20':
        dia = 'veinte'
    elif dia == '21':
        dia = 'veintiun'
    elif dia == '22':
        dia ='veintidos'
    elif dia == '23':
        dia = 'veintitres'
    elif dia == '24':
        dia ='veinticuatro'
    elif dia == '25':
        dia = 'veinticinco'
    elif dia == '26':
        dia ='veintiseis'
    elif dia == '27':
        dia = 'veintisiete'
    elif dia == '28':
        dia = 'veintiocho'
    elif dia == '29':
        dia ='veintinueve'
    elif dia == '30':
        dia = 'treinta'
    elif dia == '31':
        dia = 'treinta y un'
    return dia    