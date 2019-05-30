# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

# imports views generics 
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView, View

from apps.tecnico.models import Operador_Nuevo, Vehiculo_Nuevo, Ruta, Docs_Legal, Checklist_Vehiculo
from apps.tramite.models import Tramite, Asignar_Vehiculo
from datetime import datetime, date, timedelta
class index(TemplateView):
    template_name = 'tramite/index.html'

    def get_context_data(self, *args, **kwargs):
        context = super(index, self).get_context_data(*args, **kwargs)
        
        vehiculos = Vehiculo_Nuevo.objects.filter(es_nuevo=False)
        # print('fffffffffffff'+ str(vehiculos))
        context['vehiculos'] = vehiculos
        vehiculos_tarjeta = Asignar_Vehiculo.objects.all()
        # dias = timedelta(days=366)
        hoy = datetime.now().date()
        # print (".......-------------"+ str(hoy))
        for vehi in vehiculos_tarjeta:
            if vehi.valida_del and vehi.valida_al:
                avance_dias = hoy - vehi.valida_del
                tarjeta_del = vehi.valida_del
                tarjeta_del = tarjeta_del + avance_dias
                tarjeta_al = vehi.valida_al
                if tarjeta_del >= tarjeta_al and vehi.caducado == False:
                    vehi.caducado = True
                    vehi.save()
                    print "Tarjeta fenecida"
                # print tarjeta_al
                # print tarjeta_del

        limite_dias_notificacion = timedelta(days=371) #se esta sumando un anio mas cinco dias
        validez_tarjeta = timedelta(days=366) #dias validos
        id_tarjetas = []
        for vehi in vehiculos_tarjeta:
            if vehi.valida_del and vehi.valida_al:
                limite_avance_dias = hoy - vehi.valida_del
                if vehi.caducado == True:
                    if limite_avance_dias>=validez_tarjeta and limite_avance_dias<=limite_dias_notificacion:
                        id_tarjetas.append(vehi.vehiculo_id)

        if id_tarjetas:
            vehis_con_tarjeta_caducada = Vehiculo_Nuevo.objects.filter(es_nuevo=False, id__in=id_tarjetas)
            context['tarjetas_caducadas'] = vehis_con_tarjeta_caducada

        return context
  