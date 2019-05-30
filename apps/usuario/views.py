# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from django.core.urlresolvers import reverse_lazy

from apps.operario.models import Requisitos_RS, Razon_Social
 
from apps.usuario.form import RegistroForm, RazonSForm, RequisitosRSForm, UserProfileForm
# Create your views here.
class RegistroUsuario(CreateView):
    model = User
    template_name = 'usuario/registrar.html'
    form_class = RegistroForm
    success_url = reverse_lazy('usuario:listar')

class ListarUsuario(ListView):
    model = User
    template_name = 'usuario/listar.html'

class UserProfileUpdateView(UpdateView):
    model = User
    template_name = 'usuario/actualizar.html'
    success_url = reverse_lazy('usuario:listar')
    def get_initial(self):
        initial = super(UserProfileUpdateView, self).get_initial()
        try:
            current_group = self.object.groups.get()
        except:
            # puede ocurrir una excepción si el usuario editado no tiene grupos o tiene más de un grupo 
            # exception can occur if the edited user has no groups
            # or has more than one group
            pass
        else:
            initial['group'] = current_group.pk
        return initial
    
    def get_form_class(self):
        return UserProfileForm
    
    def form_valid(self, form):
        self.object.groups.clear()
        self.object.groups.add(form.cleaned_data['group'])
        return super(UserProfileUpdateView, self).form_valid(form)

class EliminarUsuario(DeleteView):
    model = User
    template_name = 'usuario/eliminar.html'
    success_url = reverse_lazy('usuario:listar')

#Requisitos Razon Social
class RegistrarRequisito(CreateView):
    model = Requisitos_RS
    template_name = 'usuario/requisito_razon_social_form.html'
    form_class = RequisitosRSForm
    success_url = reverse_lazy('usuario:listar_requisitoRS')

class ListarRequisito(ListView):
    model = Requisitos_RS
    template_name = 'usuario/requisito_razon_social_listar.html'

class EditarRequisito(UpdateView):
    model = Requisitos_RS
    template_name = 'usuario/requisito_razon_social_form.html'
    form_class = RequisitosRSForm
    success_url = reverse_lazy('usuario:listar_requisitoRS')

class EliminarRequisito(DeleteView):
    model = Requisitos_RS
    template_name = 'usuario/eliminar_requisito.html'
    success_url = reverse_lazy('usuario:listar_requisitoRS')

#Razon Social
class RegistroRS(CreateView):
    model = Razon_Social
    template_name = 'usuario/registrar_razon_social.html'
    form_class = RazonSForm
    success_url = reverse_lazy('usuario:listar_razon_social')

class ListarRS(ListView):
    model = Razon_Social
    template_name = 'usuario/listar_razon_social.html'

class EditarRS(UpdateView):
    model = Razon_Social
    template_name = 'usuario/registrar_razon_social.html'
    form_class = RazonSForm
    success_url = reverse_lazy('usuario:listar_razon_social')

class EliminarRS(DeleteView):
    model = Razon_Social
    template_name = 'usuario/eliminar_razon_social.html'
    success_url = reverse_lazy('usuario:listar_razon_social')
