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


def test(request):
    if request.is_ajax() or True:
        datos = json.loads(request.GET['lista_obs'])
        checks = json.loads(request.GET['lista_check'])
        ids = json.loads(request.GET['list_id'])
        for a in range(len(datos)):
            c = Checklist_Operario.objects.get(id=ids[a])
            c.observacion = None
            if len(datos[a]) > 0:
                c.observacion = datos[a]
            c.cumple = checks[a]
            c.save()
            # print ('Hola mundo, '+ str (datos[a])+ '  '+ str(checks[a])+ '  '+str(ids[a]))
        dic = {
            'response': 'ok'
        }
        return HttpResponse(json.dumps(dic), content_type='application/json')
    else:
        return HttpResponse('No permitido')

def verifivehiculo(request):
    if request.is_ajax() or True:
        datos = json.loads(request.GET['lista_obs'])
        checks = json.loads(request.GET['lista_check'])
        ids = json.loads(request.GET['list_id'])
        for a in range(len(datos)):
            c = Checklist_Vehiculo.objects.get(id=ids[a])
            c.observacion = None
            if len(datos[a]) > 0:
                c.observacion = datos[a]
            c.cumple = checks[a]
            c.save()
            # print ('Hola mundo, '+ str (datos[a])+ '  '+ str(checks[a])+ '  '+str(ids[a]))
        dic = {
            'response': 'ok'
        }
        return HttpResponse(json.dumps(dic), content_type='application/json')
    else:
        return HttpResponse('No permitido')