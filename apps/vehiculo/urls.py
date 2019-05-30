from __future__ import absolute_import
from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required
from apps.vehiculo.views import listarVehiculos, detalleVehiculos, crearInfraccion,\
search_vehiculo_placa, listarInfractores, infraccionCancelada

urlpatterns = [
        url(r'^listar/$', login_required(listarVehiculos.as_view()), name='listar_vehiculos'),
        url(r'^detalle/(?P<pk>\d+)/$', login_required(detalleVehiculos.as_view()), name='vehiculo_detalle'),
        url(r'^crear/infraccion/$', login_required(crearInfraccion.as_view()), name='crear_infraccion'),
        url(r'^search_vehiculo_placa/$', search_vehiculo_placa, name = 'search_vehiculo_placa'),
        url(r'^listar/infractores/$', login_required(listarInfractores.as_view()), name='listas_infractores'),
        url(r'^cancelando/infraccion/(?P<pk>\d+)/$', login_required(infraccionCancelada.as_view()), name='infraccion_cancelada'),
]