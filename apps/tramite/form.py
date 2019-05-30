from __future__ import unicode_literals
from __future__ import absolute_import
from django import forms
from django.contrib.admin import widgets
from apps.tramite.models import Tramite, Asignar_Vehiculo

class TramiteForm(forms.ModelForm):
    class Meta:
        model = Tramite
        fields = [
            'id',
            'tipo_tramite',
            'solicitante',
            'fecha_ingreso',
            'hora_ingreso',
            'num_fojas',
            'estado',
            'observaciones',
        ]
        labels = {
            'id': 'Nro. Tramite',
            'tipo_tramite': 'Tipo de Tramite',
            'solicitante': 'Solicitante',
            'fecha_ingreso': 'Fecha',
            'hora_ingreso': 'Hora',
            'num_fojas': 'Nro. de Fojas',
            'estado': 'Estaso',
            'observaciones': 'Observaciones',
        }
        widgets = {
            'id': forms.TextInput(attrs={'readonly':'readonly', 'class':'form-control'}),
            'tipo_tramite': forms.TextInput(attrs={'readonly':'readonly', 'class':'form-control'}),
            'solicitante': forms.TextInput(attrs={'class':'form-control has-feedback-right', 'id':'id_solicitante_ok', 'style':'display:none', 'name':'id_solicitante'}),
            'fecha_ingreso': forms.TextInput(attrs={'name':'fecha', 'id':'fechaActual', 'readonly':'readonly'}),
            'hora_ingreso': forms.TextInput(attrs={'name':'hora', 'id':'horaActual', 'readonly':'readonly'}),
            'num_fojas':forms.TextInput(attrs={'type':'number', 'id':'number', 'name':'number', 'data-validate-minmax':'0,1000', 'min':'1', 'pattern':'^[0-9]+', 'class':'form-control'}),
            'estado': forms.Select(choices = (
                                    ('INGRESADO', ('INGRESADO')),
                                    ), attrs={'class':'form-control'}),
            # 'estado': forms.Select(choices = (
            #                         ('INGRESADO', ('INGRESADO')),
            #                         ('PROCESO', ('PROCESO')),
            #                         ('ANULADO', ('ANULADO')),
            #                         ('ENTREGADO', ('ENTREGADO')),
            #                         ), attrs={'class':'form-control'}),
            'observaciones': forms.TextInput(attrs={'readonly':'readonly', 'class':'form-control'}),
        }

class AsignacionForm(forms.ModelForm):
    class Meta:
        model = Asignar_Vehiculo
        fields = [
            'id',
            'tramite',
            'vehiculo',
            'validez',
            'gestion',
            'monto',
        ]
        labels = {
            'id': 'Nro. Asignacion',
            'tramite': 'Tramite',
            'vehiculo': 'Vehiculo',
            'validez': 'Validez',
            'gestion': 'Gestion',
            'monto': 'Monto en bolivianos',
        }
        widgets = {
            'vehiculo': forms.TextInput(attrs={'class':'form-control has-feedback-right', 'id':'id_vehiculo_ok', 'style':'display:none', 'name':'id_vehiculo'}),
            'validez': forms.TextInput(attrs={'class':'form-control', 'readonly':'readonly'}),
            'gestion': forms.TextInput(attrs={'class':'form-control', 'readonly':'readonly'}),
            'monto':forms.TextInput(attrs={'type':'number', 'id':'number', 'data-validate-minmax':'0,1000', 'min':'1', 'pattern':'^[0-9]+', 'class':'form-control'}),
        }