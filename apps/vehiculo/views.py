# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect

from apps.tecnico.models import Vehiculo_Nuevo, Operador_Nuevo, Fotos_Vehiculo
from apps.tramite.models import Tramite, Asignar_Vehiculo
from apps.tecnico.models import Infraccion

from apps.vehiculo.form import InfraccionForm

from django.views.generic import CreateView, ListView, TemplateView, DetailView, UpdateView
import json
import time
import datetime
# Create your views here.

class listarVehiculos(ListView):
    model = Vehiculo_Nuevo
    template_name = 'vehiculo/lista_vehiculos.html'
    
    def get_context_data(self, *args, **kwargs):
        context = super(listarVehiculos, self).get_context_data(*args, **kwargs)
        vehiculos = Vehiculo_Nuevo.objects.filter(es_nuevo=False)
        context['vehiculos'] = vehiculos
        return context

class detalleVehiculos(DetailView):
    model = Vehiculo_Nuevo
    template_name = 'vehiculo/detalle_vehiculos.html'
    
    def get_context_data(self, *args, **kwargs):
        context = super(detalleVehiculos, self).get_context_data(*args, **kwargs)
        vehiculo = Vehiculo_Nuevo.objects.get(id = self.kwargs['pk'])
        operador = Operador_Nuevo.objects.get(id = vehiculo.operador_id)
        context['operador'] = operador
        
        fotos = Fotos_Vehiculo.objects.filter(vehiculo= vehiculo.id)
        context['fotos'] = fotos

        if Tramite.objects.filter(solicitante_id=operador.id, vigente=True).exists():
            if Tramite.objects.filter(solicitante_id=operador.id, vigente=True).count()==1:
                tramite = Tramite.objects.get(solicitante_id=operador.id, vigente=True)
            else:
                sms = 'Tramite no encontrado'
                tramite=None
            if tramite:
                # vehiculo_asignado = Asignar_Vehiculo.objects.filter(vehiculo=vehiculo.id, tramite_id=tramite.id)
                vehiculo_asignado = Asignar_Vehiculo.objects.get(vehiculo_id=vehiculo.id, tramite_id=tramite.id)

                context['detalle'] = vehiculo_asignado
        return context

class historialTarjetasVehiculo(ListView):
    model = Asignar_Vehiculo
    template_name = 'vehiculo/historial_vehiculo.html'

    def get_queryset(self, *args, **kwargs):
        queryset = super(historialTarjetasVehiculo, self).get_queryset()
        return queryset.filter(vehiculo = self.kwargs['fk'])
        
# class historialTarjetasVehiculo(ListView):
#     model = Asignar_Vehiculo
#     template_name = 'vehiculo/detalle_vehiculos.html'
    
#     def get_context_data(self, *args, **kwargs):
#         context = super(detalleVehiculos, self).get_context_data(*args, **kwargs)
#         vehiculo = Vehiculo_Nuevo.objects.get(id = self.kwargs['pk'])
#         operador = Operador_Nuevo.objects.get(id = vehiculo.operador_id)
#         context['operador'] = operador
        
#         fotos = Fotos_Vehiculo.objects.filter(vehiculo= vehiculo.id)
#         context['fotos'] = fotos

#         if Tramite.objects.filter(solicitante_id=operador.id, vigente=True).exists():
#             if Tramite.objects.filter(solicitante_id=operador.id, vigente=True).count()==1:
#                 tramite = Tramite.objects.get(solicitante_id=operador.id, vigente=True)
#             else:
#                 sms = 'Tramite no encontrado'
#                 tramite=None
#             if tramite:
#                 # vehiculo_asignado = Asignar_Vehiculo.objects.filter(vehiculo=vehiculo.id, tramite_id=tramite.id)
#                 vehiculo_asignado = Asignar_Vehiculo.objects.get(vehiculo_id=vehiculo.id, tramite_id=tramite.id)

#                 context['detalle'] = vehiculo_asignado
#         return context

class listarInfractores(ListView):
    model = Infraccion
    template_name = 'vehiculo/listar_infractores.html'

    def get_context_data(self, *args, **kwargs):
        context = super(listarInfractores, self).get_context_data(*args, **kwargs)
        infractores_vigentes = Infraccion.objects.filter(cancelado=False)
        context['infractores_vigentes'] = infractores_vigentes
        
        historial_infractores = Infraccion.objects.filter(cancelado=True)
        context['historial_infractores'] = historial_infractores

        return context

class crearInfraccion(CreateView):
    model = Infraccion
    template_name = 'vehiculo/crear_infraccion.html'
    form_class = InfraccionForm
    success_url = reverse_lazy('vehiculo:listas_infractores')

def search_vehiculo_placa(request):
    if request.is_ajax():
        vehiculos = Vehiculo_Nuevo.objects.filter(es_nuevo=False, placa__icontains = request.GET['placa']).values('id', 'placa')[:10]
        if len(vehiculos) == 0:
            return HttpResponse(
                json.dumps([{'id': 'X',
                             'placa': 'No se encontro coincidencias',
                            },]),
                content_type = 'application/json'
            )
        return HttpResponse(json.dumps(list(vehiculos)), content_type='application/json')
    else:
        return HttpResponse("Solo Ajax")

class infraccionCancelada(UpdateView):
    model = Infraccion
    template_name = 'vehiculo/infraccion_cancelada.html'
    form_class = InfraccionForm
    def form_valid(self, form):
        infraccion = Infraccion.objects.get(id=self.object.id)
        infraccion.cancelado = True
        infraccion.save()
        return HttpResponseRedirect(reverse_lazy('vehiculo:listas_infractores'))