from __future__ import absolute_import
from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required
from django.contrib import admin

from apps.operario.views import Listar_Operadores, Registrar_Operador,\
Listar_Detalle_Operadores, Detalle_Operadores, Registrar_Vehiculo,\
CrearRuta, EliminarRuta, Actualizar_Vehiculo, Eliminar_Vehiculo,\
Actualizar_Operador, Eliminar_Operador, ReportAnualOperador

urlpatterns = [
    # url(r'^editar/(?P<pk>\d+)$', RepresentanteUpdate.as_view(), name='operario_editar'),
    url(r'^listar/operadores/$', login_required(Listar_Operadores.as_view()), name='listar_operadores_nuevos'),
    url(r'^registrar/operador/(?P<pk>\d+)/$', login_required(Registrar_Operador.as_view()), name='registar_operador'),
    url(r'^listar/$', login_required(Listar_Detalle_Operadores.as_view()), name='operador_listar'),
    url(r'^detalle/(?P<pk>\d+)/$', login_required(Detalle_Operadores.as_view()), name='operadores_detalle'),
    url(r'^actualizar/(?P<pk>\d+)/$', login_required(Actualizar_Operador.as_view()), name='operador_actualizar'),
    url(r'^eliminar/(?P<pk>\d+)/$', login_required(Eliminar_Operador.as_view()), name='operador_eliminar'),

    url(r'^vehiculo/registrar/(?P<pk>\d+)/(?P<fk>\d+)/$', login_required(Registrar_Vehiculo.as_view()), name='vehiculo_registrar'),
    url(r'^vehiculo/actualizar/(?P<pk>\d+)/(?P<fk>\d+)/$', login_required(Actualizar_Vehiculo.as_view()), name='vehiculo_actualizar'),
    url(r'^vehiculo/eliminar/(?P<pk>\d+)/(?P<fk>\d+)/$', login_required(Eliminar_Vehiculo.as_view()), name='vehiculo_eliminar'),
    
    url(r'^ruta/registrar/(?P<pk>\d+)/$', login_required(CrearRuta.as_view()), name='crear_ruta'),
    url(r'^ruta/eliminar/(?P<pk>\d+)/(?P<fk>\d+)/$', login_required(EliminarRuta.as_view()), name='eliminar_ruta'),
    
    url(r'^reporte/anual/$', login_required(ReportAnualOperador.as_view()), name='reporte_anual_operador'),
]
