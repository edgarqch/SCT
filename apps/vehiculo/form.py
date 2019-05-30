from __future__ import unicode_literals
from __future__ import absolute_import
from django import forms
from django.contrib.admin import widgets

from apps.tecnico.models import Infraccion

class InfraccionForm(forms.ModelForm):
    class Meta:
        model = Infraccion
        fields = [
            'vehiculo',
            'lugar',
            'tipo',
            'observacion',
            'licencia',
            'fecha',
        ]
        labels = {
            'vehiculo': 'Vehiculo',
            'lugar': 'Lugar',
            'tipo': 'Tipo',
            'observacion': 'Observacion',
            'licencia': 'Licencia del conductos',
            'fecha': 'Fecha',
        }
        widgets = {
            'vehiculo': forms.TextInput(attrs={'class':'form-control has-feedback-right', 'id':'id_vehiculo_ok', 'style':'display:none', 'name':'id_solicitante'}),
            'lugar': forms.TextInput(attrs={'class':'form-control'}),
            'tipo': forms.TextInput(attrs={'class':'form-control'}),
            'observacion': forms.TextInput(attrs={'class':'form-control'}),
            'licencia':forms.TextInput(attrs={'class':'form-control'}),
            'fecha': forms.TextInput(attrs={'name':'fecha', 'id':'fechaActual', 'readonly':'readonly'}),
            }