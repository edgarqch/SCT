from __future__ import absolute_import
from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required
from django.contrib import admin

from apps.tecnico.views import OperarioNuevoCreate, ListarOperarioN, OperarioNuevoDetail, CrearVehiculoN,\
EditarVehiculoN, EliminarVehivuloN, VerificarOperarioN, VerificarOperario, VerificarVehiculo, NotaCreate,\
NotaEdit, CreateFoto, DeleteFoto, CreateInforme, informeObs, informeDevol, informeTecnico, EmitirDocumentos,\
createDocLegal, generar_inf_legal, generar_res_administrativa, ListarOperadorR, buscar_operador,\
SelectOperadores, RenovarTarjetas, NotaRenovacion, NotaEditRenovacion, AsignarVehiculosRenovacion,\
SeleccionarVehiculoRenovacion, QuitarVehiculoRenovacion, DetalleOperadorRenovacion, VerificarVehiculoRenovacion,\
CreateInformeRenovacion, informeObsRenovando, informeDevol_renovacion, informeTecnico_renovacion,\
crearDocLeg, CreateVehiculoN, CrearFoto, EliminarFoto, EditVehiculoN, DeleteVehivuloN, ListarMarca, CreateMarca,\
DeleteMarca

from apps.tecnico.ajax import test, verifivehiculo

urlpatterns = [
    url(r'^nuevo$', login_required(OperarioNuevoCreate.as_view()), name='operario_nuevo_crear'),
    url(r'^nueva/nota/(?P<pk>\d+)/$', login_required(NotaCreate.as_view()), name='nota_crear'),
    url(r'^editar/nota/(?P<pk>\d+)/(?P<fk>\d+)/$', login_required(NotaEdit.as_view()), name='nota_editar'),

    url(r'^listar$', login_required(ListarOperarioN.as_view()), name='operario_nuevo_listar'),
    url(r'^verificar$', login_required(VerificarOperarioN.as_view()), name='operario_nuevo_verificar'),
    url(r'^detalle/(?P<pk>\d+)/$', login_required(OperarioNuevoDetail.as_view()), name='operario_detalle'),

    url(r'^vehiculo_nuevo/(?P<pk>\d+)/$', login_required(CrearVehiculoN.as_view()), name='vehiculo_nuevo_crear'),
    url(r'^vehiculo_nuevo_editar/(?P<pk>\d+)/(?P<fk>\d+)/$', login_required(EditarVehiculoN.as_view()), name='vehiculo_nuevo_editar'),
    url(r'^vehiculo_nuevo_eliminar/(?P<pk>\d+)/(?P<fk>\d+)/$', login_required(EliminarVehivuloN.as_view()), name='vehiculo_nuevo_eliminar'),

    url(r'^verificacion/(?P<pk>\d+)/$', login_required(VerificarOperario.as_view()), name='operador_verificacion'),
    
    url(r'^verifi/(?P<pk>\d+)/$', login_required(VerificarVehiculo.as_view()), name='vehiculo_verificacion'),
    # funciones ajax
    url(r'^prueba$', test, name='prueba'),
    url(r'^verificarvehiculo$', verifivehiculo, name='verificar_vehiculo'),
    # url fotos vehiculos
    url(r'^foto_vehiculo/(?P<pk>\d+)/$', login_required(CreateFoto.as_view()), name='foto_vehiculo'),
    url(r'^foto_eliminar/(?P<pk>\d+)/(?P<fk>\d+)/$', login_required(DeleteFoto.as_view()), name='foto_eliminar'),

    # url emitir informes
    url(r'^informe/(?P<pk>\d+)/(?P<tip>\d+)/$', login_required(CreateInforme.as_view()), name='emitir_informe'),
    url(r'^informeobs/(?P<pk>\d+)/$', login_required(informeObs.as_view()), name='informe_obs'),
    url(r'^informedevol/(?P<pk>\d+)/$', login_required(informeDevol.as_view()), name='informe_devol'),
    url(r'^informetecnico/(?P<pk>\d+)/$', login_required(informeTecnico.as_view()), name='informe_tecnico'),

    # Documentos Legales
    url(r'^listar/op/documentos/$', login_required(EmitirDocumentos.as_view()), name='listar_op_documentos'),
    url(r'^listar/op/documentos/informelegal/(?P<pk>\d+)/(?P<tip>\d+)/$', login_required(createDocLegal.as_view()), name='doc_legal'),

    url(r'^generar/informelegal/(?P<pk>\d+)/$', login_required(generar_inf_legal), name='generar_informe_legal'),
    url(r'^generar/resadministrativa/(?P<pk>\d+)/$', login_required(generar_res_administrativa), name='generar_resolucion_administrativa'),

    url(r'^listarRenovados$', login_required(ListarOperadorR.as_view()), name='operador_renovavion_listar'),
    # Intento, de poner un operador para renovacion de tarjetas
    url(r'^buscar_operador/$', buscar_operador, name = 'buscar_operador'),
    # fin intento
    url(r'^operadores/$', login_required(SelectOperadores.as_view()), name='seleccionar_operadores'),
    url(r'^renovar/(?P<pk>\d+)/$', login_required(RenovarTarjetas.as_view()), name='renovar_operador'),

    url(r'^nota/(?P<pk>\d+)/$', login_required(NotaRenovacion.as_view()), name='nota_renovar'),
    url(r'^nota/editar/(?P<pk>\d+)/(?P<fk>\d+)/$', login_required(NotaEditRenovacion.as_view()), name='nota_renovacion_editar'),

    url(r'^asignar/renovacion/(?P<pk>\d+)/$', login_required(AsignarVehiculosRenovacion.as_view()), name='operador_renovacion'),
    url(r'^renovar/vehiculo/(?P<pk>\d+)/$', login_required(SeleccionarVehiculoRenovacion.as_view()), name='vehiculo_renovar'),
    url(r'^quitar/vehiculo/(?P<pk>\d+)/$', login_required(QuitarVehiculoRenovacion.as_view()), name='vehiculo_quitar'),
    url(r'^detalle/renovacion/(?P<pk>\d+)/$', login_required(DetalleOperadorRenovacion.as_view()), name='operador_renovando'),
    url(r'^vehiculo/renovacion/(?P<pk>\d+)/$', login_required(VerificarVehiculoRenovacion.as_view()), name='vehiculo_renovando'),

    url(r'^informe/renovacion/(?P<pk>\d+)/$', login_required(informeObsRenovando.as_view()), name='informe_obs_renovando'),
    url(r'^informe/devolucion/(?P<pk>\d+)/$', login_required(informeDevol_renovacion.as_view()), name='informe_devol_renovando'),
    url(r'^informe/tecnico/(?P<pk>\d+)/$', login_required(informeTecnico_renovacion.as_view()), name='informe_tecnico_renovando'),
    url(r'^informe/r/(?P<pk>\d+)/(?P<tip>\d+)/$', login_required(CreateInformeRenovacion.as_view()), name='emitir_informe_renovacion'),

    url(r'^documento/legal/(?P<pk>\d+)/(?P<tip>\d+)/$', login_required(crearDocLeg.as_view()), name='documento_legal'),

    #Aumetar vehiculos al renovar
    url(r'^nuevo_vehiculo/(?P<pk>\d+)/$', login_required(CreateVehiculoN.as_view()), name='crear_vehiculo_nuevo'),
    url(r'^vehiculo_n_editar/(?P<pk>\d+)/(?P<fk>\d+)/$', login_required(EditVehiculoN.as_view()), name='vehiculo_n_editar'),
    url(r'^vehiculo_n_eliminar/(?P<pk>\d+)/(?P<fk>\d+)/$', login_required(DeleteVehivuloN.as_view()), name='vehiculo_n_eliminar'),

    url(r'^foto_vehi/(?P<pk>\d+)/$', login_required(CrearFoto.as_view()), name='foto_vehi'),
    url(r'^foto_delete/(?P<pk>\d+)/(?P<fk>\d+)/$', login_required(EliminarFoto.as_view()), name='eliminar_foto'),
    url(r'^marca/listar/$', login_required(ListarMarca.as_view()), name='listar_marca'),
    url(r'^create_marca/$', login_required(CreateMarca.as_view()), name='crear_marca'),
    url(r'^delete_marca/(?P<pk>\d+)/$', login_required(DeleteMarca.as_view()), name='eliminar_marca'),

]