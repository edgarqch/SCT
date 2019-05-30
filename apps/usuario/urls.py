from __future__ import absolute_import
from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required

from apps.usuario.views import RegistroUsuario, ListarUsuario, EliminarUsuario,\
RegistrarRequisito,ListarRequisito, EditarRequisito ,EliminarRequisito , RegistroRS, ListarRS,\
EditarRS, EliminarRS, UserProfileUpdateView

urlpatterns = [
    url(r'^registrar', login_required(RegistroUsuario.as_view()), name='registrar'),
    url(r'^listar', login_required(ListarUsuario.as_view()), name='listar'),
    # url(r'^editar/(?P<pk>\d+)/$', login_required(EditarUsuario.as_view()), name='editar'),
    url(r'^editar/(?P<pk>\d+)/$', login_required(UserProfileUpdateView.as_view()), name='editar'),
    url(r'^eliminar/(?P<pk>\d+)/$', login_required(EliminarUsuario.as_view()), name='eliminar'),
    
    url(r'^requisito/rs/registrar/', login_required(RegistrarRequisito.as_view()), name='registrar_requisitoRS'),
    url(r'^requisito/rs/listar/', login_required(ListarRequisito.as_view()), name='listar_requisitoRS'),
    url(r'^requisito/editar/(?P<pk>\d+)/$', login_required(EditarRequisito.as_view()), name='editar_requisito'),
    url(r'^requisito/eliminar/(?P<pk>\d+)/$', login_required(EliminarRequisito.as_view()), name='eliminar_requisito'),
    
    url(r'^razon_social/registrar/', login_required(RegistroRS.as_view()), name='registrar_razon_social'),
    url(r'^razon_social/listar/', login_required(ListarRS.as_view()), name='listar_razon_social'),
    url(r'^razon_social/editar/(?P<pk>\d+)/$', login_required(EditarRS.as_view()), name='editar_razon_social'),
    url(r'^razon_social/eliminar/(?P<pk>\d+)/$', login_required(EliminarRS.as_view()), name='eliminar_razon_social'),
]
