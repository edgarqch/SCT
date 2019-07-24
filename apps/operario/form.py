from __future__ import unicode_literals
from __future__ import absolute_import
from django import forms
from django.contrib.admin import widgets
# from apps.operario.models import Rep_Legal

from apps.tecnico.models import Vehiculo_Nuevo, Operador_Nuevo

class VehiculoForm(forms.ModelForm):

    class Meta:
        model = Vehiculo_Nuevo
        fields = [
            'id',
            'operador',
            'tipo',
            'propietario',
            'placa',
            'tipo_vehiculo',
            'marca',
            'modelo',
            'chasis',
            'capacidad',
            'color',
        ] 
        labels = {
            'operador': 'Operador',
            'tipo': 'Tipo',
            'propietario': 'Propietario',
            'placa': 'Placa',
            'tipo_vehiculo': 'Tipo de Vehiculo',
            'marca': 'Marca',
            'modelo': 'Modelo',
            'chasis': 'Chasis',
            'capacidad': 'Capacidad',
            'color': 'Color',
        }
        widgets = {
            'operador': forms.Select(attrs={'class':'form-control', 'disabled':'disabled'}),
            'tipo': forms.Select(attrs={'class':'form-control', 'disabled':'disabled'}),
            'propietario': forms.TextInput(attrs={'class':'form-control'}),
            'placa': forms.TextInput(attrs={'class':'form-control'}),
            'tipo_vehiculo': forms.Select(choices = (
                 ('OMNIBUS', ('OMNIBUS')),
                 ('MICROBUS', ('MICROBUS')),
                 ('MINIBUS', ('MINIBUS')),
                 ('VAGONETA', ('VAGONETA')),
                 ('CAMIONETA', ('CAMIONETA')),
                 ('AUTOMOVIL', ('AUTOMOVIL')),
                 ('CAMION', ('CAMION')),
                 ('TRACTO CAMION', ('TRACTO CAMION')),
                 ), attrs={'class':'form-control'}),
            'marca': forms.Select(choices = (
                 ('AGRALE', ('AGRALE')),
                 ('ASIA', ('ASIA')),
                 ('BCH', ('BCH')),
                 ('CHEVROLET', ('CHEVROLET')),
                 ('DAIMLER', ('DAIMLER')),
                 ('DODGE', ('DODGE')),
                 ('FARGO', ('FARGO')),
                 ('FIAT', ('FIAT')),
                 ('FORD', ('FORD')),
                 ('FREIGHTLINER', ('FREIGHTLINER')),
                 ('GEO', ('GEO')),
                 ('GMC', ('GMC')),
                 ('HINO', ('HINO')),
                 ('HYUNDAI', ('HYUNDAI')),
                 ('INTERNATIONAL', ('INTERNATIONAL')),
                 ('ISUZU', ('ISUZU')),
                 ('IVECO', ('IVECO')),
                 ('JIEFANG', ('JIEFANG')),
                 ('KAMAZ', ('KAMAZ')),
                 ('KIA', ('KIA')),
                 ('LEYLAND', ('LEYLAND')),
                 ('MACK', ('MACK')),
                 ('MAZ', ('MAZ')),
                 ('MAZDA', ('MAZDA')),
                 ('MERCEDES BENZ', ('MERCEDES BENZ')),
                 ('MITSUBISHI', ('MITSUBISHI')),
                 ('NEOPLAN', ('NEOPLAN')),
                 ('NISSAN', ('NISSAN')),
                 ('PACIFIC', ('PACIFIC')),
                 ('PEGASO', ('PEGASO')),
                 ('RENAULT', ('RENAULT')),
                 ('SAURER', ('SAURER')),
                 ('SCANIA', ('SCANIA')),
                 ('SELIGSON', ('SELIGSON')),
                 ('SSANG YONG', ('SSANG YONG')),
                 ('TOYOTA', ('TOYOTA')),
                 ('VOLKSWAGEN', ('VOLKSWAGEN')),
                 ('VOLVO', ('VOLVO')),
                 ), attrs={'class':'form-control'}),
            'modelo': forms.TextInput(attrs={'type':'number' ,'class':'form-control'}),
            'chasis': forms.TextInput(attrs={'class':'form-control'}),
            'capacidad': forms.TextInput(attrs={'class':'form-control'}),
            'color': forms.TextInput(attrs={'class':'form-control'}),
        }

class VehiRegisterForm(forms.ModelForm):

    class Meta:
        model = Vehiculo_Nuevo
        fields = [
            'id',
            'operador',
            'tipo',
            'propietario',
            'placa',
            'tipo_vehiculo',
            'marca',
            'modelo',
            'chasis',
            'capacidad',
            'color',
        ] 
        labels = {
            'operador': 'OPERADOR',
            'tipo': 'TIPO',
            'propietario': 'PROPIETARIO',
            'placa': 'PLACA',
            'tipo_vehiculo': 'TIPO DE VEHICULO',
            'marca': 'MARCA',
            'modelo': 'MODELO',
            'chasis': 'CHASIS',
            'capacidad': 'CAPACIDAD',
            'color': 'COLOR',
        }
        widgets = {
            'operador': forms.Select(attrs={'class':'form-control'}),
            'tipo': forms.Select(attrs={'class':'form-control'}),
            'propietario': forms.TextInput(attrs={'class':'form-control', 'readonly':'readonly'}),
            'placa': forms.TextInput(attrs={'class':'form-control', 'readonly':'readonly'}),
            'tipo_vehiculo': forms.TextInput(attrs={'class':'form-control', 'readonly':'readonly'}),
            'marca': forms.Select(attrs={'class':'form-control'}),
            'modelo': forms.TextInput(attrs={'type':'number' ,'class':'form-control', 'pattern':'^[0-9]+', 'min':'1970'}),
            'chasis': forms.TextInput(attrs={'class':'form-control', 'onkeyup':'javascript:this.value=this.value.toUpperCase();'}),
            'capacidad': forms.TextInput(attrs={'class':'form-control', 'onkeyup':'javascript:this.value=this.value.toUpperCase();'}),
            'color': forms.TextInput(attrs={'class':'form-control', 'onkeyup':'javascript:this.value=this.value.toUpperCase();'}),
        }
    def clean_chasis(self):
        chasis = self.cleaned_data.get("chasis")
        existe_vehiculo = Vehiculo_Nuevo.objects.filter(chasis=chasis).exists()
        if chasis != None:
            tieneEspacio = False
            for i in range(len(chasis)):
                if chasis[i].isspace():
                    tieneEspacio = True

        if chasis == None:
            raise forms.ValidationError("Introduzca el chasis del vehiculo")
        elif tieneEspacio:
            raise forms.ValidationError("El campo no acepta espacios en blanco")
        elif existe_vehiculo:
            raise forms.ValidationError("El chasis introducido ya pertenece a un vehiculo")
        return chasis

class OperadorForm(forms.ModelForm):

    class Meta:
        model = Operador_Nuevo
        fields = [
            'id',
            'razon_social',
            'nombre',
            'numero_registro',
            'tipo',
            'modalidad',
            'domicilio',
            'nit',
            'observaciones',
            'documento_legal',
            'digital',
        ]
        labels = {
            'razon_social': 'RAZON SOCIAL',
            'nombre': 'NOMBRE',
            'numero_registro': 'NUM. DE REGISTRO',
            'tipo': 'TIPO',
            'modalidad': 'MODALIDAD',
            'domicilio': 'DOMICILIO',
            'nit': 'NIT',
            'observaciones': 'OBSERVACION',
            'documento_legal': 'DOCUMENTOS LEGALES',
            'digital': 'DIGITAL'
        }
        widgets = {
            'razon_social': forms.Select(attrs={'class':'form-control', 'readonly':'readonly'}),
            'nombre': forms.TextInput(attrs={'class':'form-control', 'onkeyup':'javascript:this.value=this.value.toUpperCase();', 'readonly':'readonly'}),
            'numero_registro': forms.TextInput(attrs={'class':'form-control', 'type':'number', 'pattern':'^[0-9]+', 'min':'1'}),
            'tipo': forms.Select(choices = (
                ('PASAJEROS', ('PASAJEROS')),
                ('CARGA', ('CARGA')),
                ), attrs={'class':'form-control'}),
            'modalidad': forms.Select(choices = (
                 ('OMNIBUS', ('OMNIBUS')),
                 ('MICROBUS', ('MICROBUS')),
                 ('MINIBUS', ('MINIBUS')),
                 ('VAGONETA', ('VAGONETA')),
                 ('CAMIONETA', ('CAMIONETA')),
                 ('AUTOMOVIL', ('AUTOMOVIL')),
                 ('CAMION', ('CAMION')),
                 ('TRACTO CAMION', ('TRACTO CAMION')),
                 ('MIXTO', ('MIXTO')),
                 ), attrs={'class':'form-control'}),
            'domicilio': forms.TextInput(attrs={'class':'form-control', 'onkeyup':'javascript:this.value=this.value.toUpperCase();'}),
            'nit': forms.TextInput(attrs={'type':'number', 'class':'form-control', 'pattern':'^[0-9]+', 'min':'1'}),
            'observaciones': forms.Textarea(attrs={'class':'form-control', 'rows':'2', 'cols':'50'}),
            'documento_legal': forms.TextInput(attrs={'class':'form-control', 'onkeyup':'javascript:this.value=this.value.toUpperCase();'}),
            'digital': forms.FileInput(),
        }

class OpRegisterForm(forms.ModelForm):
    class Meta:
        model = Operador_Nuevo
        fields = [
            'razon_social',
            'nombre',
            'numero_registro',
            'tipo',
            'modalidad',
            'domicilio',
            'nit',
            'observaciones',
            'documento_legal',
            'digital',
        ]
        labels = {
            'razon_social': 'RAZON SOCIAL',
            'nombre': 'NOMBRE',
            'numero_registro': 'NUMERO DE REGISTRO',
            'tipo': 'TIPO',
            'modalidad': 'MODALIDAD',
            'domicilio': 'DOMICILIO',
            'nit': 'Nro. De NIT',
            'observaciones': 'OBSERVACIONES',
            'documento_legal': 'DOCUMENTOS LEGALES',
            'digital': 'DIGITAL',
        }
        widgets = {
             'razon_social': forms.TextInput(attrs={'class':'form-control', 'readonly':'readonly'}),
             'nombre': forms.TextInput(attrs={'class':'form-control', 'readonly':'readonly'}),
             'numero_registro': forms.TextInput(attrs={'type':'number', 'class':'form-control', 'pattern':'^[0-9]+', 'min':'1'}),
             'tipo': forms.Select(choices = (
                 ('Pasajeros', ('PASAJEROS')),
                 ('Carga', ('CARGA')),
                 ), attrs={'class':'form-control'}),
             'modalidad': forms.Select(choices = (
                 ('OMNIBUS', ('OMNIBUS')),
                 ('MICROBUS', ('MICROBUS')),
                 ('MINIBUS', ('MINIBUS')),
                 ('VAGONETA', ('VAGONETA')),
                 ('CAMIONETA', ('CAMIONETA')),
                 ('AUTOMOVIL', ('AUTOMOVIL')),
                 ('CAMION', ('CAMION')),
                 ('TRACTO CAMION', ('TRACTO CAMION')),
                 ('MIXTO', ('MIXTO')),
                 ), attrs={'class':'form-control'}),
             'domicilio':forms.TextInput(attrs={'class':'form-control', 'onkeyup':'javascript:this.value=this.value.toUpperCase();'}),
             'nit':forms.TextInput(attrs={'type':'number', 'class':'form-control', 'pattern':'^[0-9]+', 'min':'1'}),
             'observaciones':forms.Textarea(attrs={'class':'form-control', 'rows':'2', 'cols':'50'}),
             'documento_legal':forms.TextInput(attrs={'class':'form-control', 'onkeyup':'javascript:this.value=this.value.toUpperCase();'}),
             'digital':forms.FileInput(),
        }
    def clean_nit(self):
        nit = self.cleaned_data.get("nit")
        if nit == None:
            raise forms.ValidationError("Por favor Inserte un valor")
        return nit

    def clean(self):
        super(OpRegisterForm, self).clean()
        data = self.cleaned_data
        if data["razon_social"] == None:
            raise forms.ValidationError({'razon_social': ["Elija una opcion."]})
        return data

# class OperarioForm(forms.ModelForm):

#     class Meta:
#         model = Operario
#         fields = [
#             'razon_social',
#             'numero_registro',
#             'nombre',
#             'modalidad',
#             'domicilio',
#             'nit',
#             'tipo',
#             'ruta',
#             'observaciones',
#             'documento_legal',
#             'digital'
#         ]
#         labels = {
#             'razon_social': 'Razon Social', 
#             'numero_registro': 'Numero de Registro',
#             'nombre': 'Nombre',
#             'modalidad': 'Modalidad',
#             'domicilio': 'Domicilio Legal',
#             'nit': 'NIT',
#             'tipo': 'Tipo de transporte',
#             'ruta': 'Ruta Actual',
#             'observaciones': 'Observaciones',
#             'documento_legal': 'Documento Legal',
#             'digital': 'Doc. Digital',
#         }
#         widgets = {
#              'razon_social': forms.Select(attrs={'class':'form-control'}),
#              'numero_registro': forms.TextInput(attrs={'type':'number', 'class':'form-control'}),
#              'nombre': forms.TextInput(attrs={'class':'form-control'}),
#              'modalidad': forms.TextInput(attrs={'class':'form-control'}),
#              'domicilio':forms.TextInput(attrs={'class':'form-control'}),
#              'nit':forms.TextInput(attrs={'type':'number', 'class':'form-control'}),
#              'tipo': forms.Select(choices = (
#                  ('Pasajeros', ('PASAJEROS')),
#                  ('Carga', ('CARGA')),
#                  ), attrs={'class':'form-control'}),
#              'ruta':forms.Textarea(attrs={'class':'form-control', 'rows':'3', 'cols':'50'}),
#              'observaciones':forms.Textarea(attrs={'class':'form-control', 'rows':'2', 'cols':'50'}),
#              'documento_legal':forms.TextInput(attrs={'class':'form-control'}),
#              'digital':forms.FileInput(),
#         }

# class RepresentanteForm(forms.ModelForm):

#     class Meta:
#         model = Rep_Legal
#         fields = [
#             'ci',
#             'nombre_r',
#             'domicilio_r',
#             'estado_activo',
#         ]
#         labels = {
#             'ci': 'CI',
#             'nombre_r': 'Nombre',
#             'domicilio_r': 'Domicilio',
#             'estado_activo': 'Estado',
#         }
#         widgets = {
#              'ci': forms.TextInput(attrs={'type':'number', 'class':'form-control'}),
#              'nombre_r': forms.TextInput(attrs={'class':'form-control'}),
#              'domicilio_r': forms.TextInput(attrs={'class':'form-control'}),
#              'estado_activo':forms.CheckboxInput(attrs={'type':'checkbox', 'class':'form-control'}),
#         }




                #  ('AGRALE', ('AGRALE')),
                #  ('ASIA', ('ASIA')),
                #  ('BCH', ('BCH')),
                #  ('CHEVROLET', ('CHEVROLET')),
                #  ('DAIMLER', ('DAIMLER')),
                #  ('DODGE', ('DODGE')),
                #  ('FARGO', ('FARGO')),
                #  ('FIAT', ('FIAT')),
                #  ('FORD', ('FORD')),
                #  ('FREIGHTLINER', ('FREIGHTLINER')),
                #  ('GEO', ('GEO')),
                #  ('GMC', ('GMC')),
                #  ('HINO', ('HINO')),
                #  ('HYUNDAI', ('HYUNDAI')),
                #  ('INTERNATIONAL', ('INTERNATIONAL')),
                #  ('ISUZU', ('ISUZU')),
                #  ('IVECO', ('IVECO')),
                #  ('JIEFANG', ('JIEFANG')),
                #  ('KAMAZ', ('KAMAZ')),
                #  ('KIA', ('KIA')),
                #  ('LEYLAND', ('LEYLAND')),
                #  ('MACK', ('MACK')),
                #  ('MAZ', ('MAZ')),
                #  ('MAZDA', ('MAZDA')),
                #  ('MERCEDES BENZ', ('MERCEDES BENZ')),
                #  ('MITSUBISHI', ('MITSUBISHI')),
                #  ('NEOPLAN', ('NEOPLAN')),
                #  ('NISSAN', ('NISSAN')),
                #  ('PACIFIC', ('PACIFIC')),
                #  ('PEGASO', ('PEGASO')),
                #  ('RENAULT', ('RENAULT')),
                #  ('SAURER', ('SAURER')),
                #  ('SCANIA', ('SCANIA')),
                #  ('SELIGSON', ('SELIGSON')),
                #  ('SSANG YONG', ('SSANG YONG')),
                #  ('TOYOTA', ('TOYOTA')),
                #  ('VOLKSWAGEN', ('VOLKSWAGEN')),
                #  ('VOLVO', ('VOLVO')),