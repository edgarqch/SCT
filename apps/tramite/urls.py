from __future__ import absolute_import
from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required

from apps.tramite.home import Index
from apps.tramite.views import CrearTramite, search_operador_nombre,\
ListarTramite, AsignarVehiculos, AsignarVehiculo, search_vehiculo_placa,\
TramiteProceso, ordenDeposito, ListarTarjetas, Tarjetas, TramiteFinalizar,\
EliminarAsignacion, ListarSeguimiento, Seguimiento
# tramite_view, tramite_list_ingresados, seguimiento_view, tramite_search, tramite_encontrar


urlpatterns = [
    url(r'^$', login_required(Index.as_view()), name='index'),
    url(r'^registrar/$', login_required(CrearTramite.as_view()), name='registrar_tramite'),
    url(r'^search_operador_nombre/$', search_operador_nombre, name = 'search_operador_nombre'),
    url(r'^listar/$', login_required(ListarTramite.as_view()), name='listar_tramite'),
    url(r'^asignarvehiculos/(?P<pk>\d+)/$', login_required(AsignarVehiculos.as_view()), name='asignar_vehiculos'),
    url(r'^asignarvehiculo/(?P<pk>\d+)/$', login_required(AsignarVehiculo.as_view()), name='asignar_vehiculo'),
    url(r'^asignacion/eliminar/(?P<pk>\d+)/(?P<fk>\d+)/$', login_required(EliminarAsignacion.as_view()), name='eliminar_asignacion'),
    url(r'^tramiteproceso/(?P<pk>\d+)/$', login_required(TramiteProceso.as_view()), name='tramite_proceso'),
    url(r'^search_vehiculo_placa/$', search_vehiculo_placa, name = 'search_vehiculo_placa'),
    url(r'^ordendeposito/(?P<pk>\d+)/$', login_required(ordenDeposito.as_view()), name='orden_deposito'),
    url(r'^tarjetas/(?P<pk>\d+)/$', login_required(ListarTarjetas.as_view()), name='tarjetas'),
    url(r'^imprimir/tarjeta/(?P<pk>\d+)/$', login_required(Tarjetas.as_view()), name='imprimir_tarjeta'),
    url(r'^finalizar/(?P<pk>\d+)/$', login_required(TramiteFinalizar.as_view()), name='tramite_finalizar'),
    url(r'^listar/seguimiento/$', login_required(ListarSeguimiento.as_view()), name='listar_seguimiento'),
    url(r'^seguimiento/(?P<pk>\d+)/$', login_required(Seguimiento.as_view()), name='seguimiento'),
]



# urlpatterns = [
    # url(r'^nuevo$', tramite_view, name='tramite_crear'),
    # url(r'^listar_ingresados$', tramite_list_ingresados, name='tramite_listar_ingresados'),
    # url(r'^seguimiento/(?P<fk>\d+)/$', seguimiento_view, name='seguimiento_crear'),
    # url(r'^buscar$', tramite_search.as_view(), name='buscar_tramite'),
    # url(r'^list_tramite_subjects$', tramite_encontrar.as_view(), name='list_tramite_subjects'),
# ]