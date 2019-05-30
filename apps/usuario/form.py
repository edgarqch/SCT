from __future__ import absolute_import
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django import forms
from apps.operario.models import Requisitos_RS, Razon_Social
from django.forms.widgets import CheckboxSelectMultiple

class RegistroForm(UserCreationForm):

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
        ]
        labels = {
            'username':'Nombre de usuario',
            'first_name':'Nombre',
            'last_name':'Apellidos',
            'email':'Correo',
        }

class UserProfileForm(forms.ModelForm):
    # group = forms.ModelChoiceField(queryset=Group.objects.all())
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'username', 'last_name', 'email', 'group']

class RequisitosRSForm(forms.ModelForm):
    class Meta:
        model = Requisitos_RS
        fields = [
            'descripcion',
        ]
        labels = {
            'descripcion':'Requisito',
        }
        widgets = {
            'descripcion': forms.Textarea(attrs={'class':'form-control', 'rows':'2', 'cols':'50'}),
        }

class RazonSForm(forms.ModelForm):

    class Meta:
        model = Razon_Social
        fields = [
            'nombre',
            'requisitos',
        ]
        labels = {
            'nombre':'Nombre',
            'requisitos':'Requisito',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class':'form-control'}),
            'requisitos': forms.CheckboxSelectMultiple(),
        }