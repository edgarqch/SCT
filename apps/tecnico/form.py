from __future__ import unicode_literals
from __future__ import absolute_import
from django import forms
from django.forms import ModelForm
from apps.tecnico.models import Operador_Nuevo, Vehiculo_Nuevo, Nota,\
Fotos_Vehiculo, Informe, Docs_Legal, Ruta
from django.contrib.admin import widgets
from apps.tecnico.models import Vehiculo_Nuevo
import time
from datetime import datetime, timedelta

class OperarioNuevoForm(forms.ModelForm):
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
             'razon_social': forms.Select(attrs={'class':'form-control'}),
             'nombre': forms.TextInput(attrs={'class':'form-control', 'onkeyup':'javascript:this.value=this.value.toUpperCase();'}),
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
             'domicilio':forms.TextInput(attrs={'class':'form-control'}),
             'nit':forms.TextInput(attrs={'type':'number', 'class':'form-control', 'pattern':'^[0-9]+', 'min':'1'}),
             'observaciones':forms.Textarea(attrs={'class':'form-control', 'rows':'2', 'cols':'50'}),
             'documento_legal':forms.TextInput(attrs={'class':'form-control'}),
             'digital':forms.FileInput(),
        }
    def clean_nombre(self):
        # email = self.cleaned_data.get("email")
        # email_base, proveeder = email.split("@")
        # dominio, extension = proveeder.split(".")
        # if not extension == "edu":
        #     raise forms.ValidationError("Por favor utiliza un email con la extension .EDU")
        # return email
        nombre = self.cleaned_data.get("nombre")
        if nombre == None:
            raise forms.ValidationError("Por favor Inserte el Nombre del Operador")
        return nombre

    def clean(self):
        super(OperarioNuevoForm, self).clean()
        data = self.cleaned_data
        if data["razon_social"] == None:
            raise forms.ValidationError({'razon_social': ["Elija una opcion."]})
        return data

class OperarioRenovarForm(forms.ModelForm):
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
             'razon_social': forms.Select(attrs={'class':'form-control'}),
             'nombre': forms.TextInput(attrs={'class':'form-control', 'onkeyup':'javascript:this.value=this.value.toUpperCase();'}),
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
             'domicilio':forms.TextInput(attrs={'class':'form-control'}),
             'nit':forms.TextInput(attrs={'type':'number', 'class':'form-control', 'pattern':'^[0-9]+', 'min':'1'}),
             'observaciones':forms.Textarea(attrs={'class':'form-control', 'rows':'2', 'cols':'50'}),
             'documento_legal':forms.TextInput(attrs={'class':'form-control'}),
             'digital':forms.FileInput(),
        }

class VehiculoNForm(forms.ModelForm):

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
            'propietario': forms.TextInput(attrs={'class':'form-control', 'onkeyup':'javascript:this.value=this.value.toUpperCase();'}),
            'placa': forms.TextInput(attrs={'class':'form-control', 'onkeyup':'javascript:this.value=this.value.toUpperCase();'}),
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
            'marca': forms.TextInput(attrs={'class':'form-control'}),
            'modelo': forms.TextInput(attrs={'type':'number' ,'class':'form-control', 'pattern':'^[0-9]+', 'min':'1960'}),
            'chasis': forms.TextInput(attrs={'class':'form-control'}),
            'capacidad': forms.TextInput(attrs={'class':'form-control'}),
            'color': forms.TextInput(attrs={'class':'form-control'}),
        }
    def clean_propietario(self):
        prop = self.cleaned_data.get("propietario")
        if prop == None:
            raise forms.ValidationError("Introduzca en nombre del propietario")
        return prop
    def clean_placa(self):
        placa = self.cleaned_data.get("placa")
        existe_vehiculo = Vehiculo_Nuevo.objects.filter(placa=placa, dar_baja=False).exists()
        if placa != None:
            tieneEspacio = False
            for i in range(len(placa)):
                if placa[i].isspace():
                    tieneEspacio = True

        if placa == None:
            raise forms.ValidationError("Introduzca la placa del vehiculo")
        elif tieneEspacio:
            raise forms.ValidationError("El campo no acepta espacios en blanco")
        elif existe_vehiculo:
            raise forms.ValidationError("Este vehiculo esta registrado en un operador, para poder registrarlo nuevamente, debe dar de baja al vehiculo...")
        return placa
    def clean_tipo_vehiculo(self):
        placa = self.cleaned_data.get("tipo_vehiculo")
        if placa == None:
            raise forms.ValidationError("Introduzca el tipo de vehiculo")
        return placa

class VehiculoRenovForm(forms.ModelForm):

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
            'propietario': forms.TextInput(attrs={'class':'form-control', 'onkeyup':'javascript:this.value=this.value.toUpperCase();'}),
            'placa': forms.TextInput(attrs={'class':'form-control', 'onkeyup':'javascript:this.value=this.value.toUpperCase();'}),
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
            'marca': forms.TextInput(attrs={'class':'form-control'}),
            'modelo': forms.TextInput(attrs={'type':'number' ,'class':'form-control', 'pattern':'^[0-9]+', 'min':'1960'}),
            'chasis': forms.TextInput(attrs={'class':'form-control'}),
            'capacidad': forms.TextInput(attrs={'class':'form-control'}),
            'color': forms.TextInput(attrs={'class':'form-control'}),
        }

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
            'propietario': forms.TextInput(attrs={'class':'form-control', 'onkeyup':'javascript:this.value=this.value.toUpperCase();'}),
            'placa': forms.TextInput(attrs={'class':'form-control', 'onkeyup':'javascript:this.value=this.value.toUpperCase();'}),
            'tipo_vehiculo': forms.TextInput(attrs={'class':'form-control', 'required':True}),
            'marca': forms.TextInput(attrs={'class':'form-control'}),
            'modelo': forms.TextInput(attrs={'type':'number' ,'class':'form-control', 'pattern':'^[0-9]+', 'min':'1960'}),
            'chasis': forms.TextInput(attrs={'class':'form-control'}),
            'capacidad': forms.TextInput(attrs={'class':'form-control'}),
            'color': forms.TextInput(attrs={'class':'form-control'}),
        }
    # def clean_propietario(self):
    #     prop = self.cleaned_data.get("propietario")
    #     if prop == None:
    #         raise forms.ValidationError("Introduzca en nombre del propietario")
    #     return prop
    # def clean_placa(self):
    #     placa = self.cleaned_data.get("placa")
    #     existe_vehiculo = Vehiculo_Nuevo.objects.filter(placa=placa, dar_baja=False).exists()
    #     if placa != None:
    #         tieneEspacio = False
    #         for i in range(len(placa)):
    #             if placa[i].isspace():
    #                 tieneEspacio = True

    #     if placa == None:
    #         raise forms.ValidationError("Introduzca la placa del vehiculo")
    #     elif tieneEspacio:
    #         raise forms.ValidationError("El campo no acepta espacios en blanco")
    #     elif existe_vehiculo:
    #         raise forms.ValidationError("Este vehiculo esta registrado en un operador, para poder registrarlo nuevamente, debe dar de baja al vehiculo...")
    #     return placa
    # def clean_tipo_vehiculo(self):
    #     placa = self.cleaned_data.get("tipo_vehiculo")
    #     if placa == None:
    #         raise forms.ValidationError("Introduzca el tipo de vehiculo")
    #     return placa

class NotaForm(forms.ModelForm):

    class Meta:
        model = Nota
        fields = [
            'operador_n',
            'cite',
            'fecha',
            'nombre_ente',
            'representante_ente',
            'cargo_repr',
            'ruta_solicitada',
            'cantidad_tarjetas',
        ]
        labels = {
            'operador_n': 'Operador',
            'cite': 'Numero de Cite',
            'fecha': 'Fecha',
            'nombre_ente': 'Nombre del Ente',
            'representante_ente': 'Representante',
            'cargo_repr': 'Cargo del Representante',
            'ruta_solicitada': 'Ruta solicitada',
            'cantidad_tarjetas': 'Cantidad de vehiculos',
        }
        hoy = datetime.now()
        dias_antes = timedelta(days= 200)
        fecha_antes = hoy - dias_antes
        if int(fecha_antes.day) < 10:
            fecha_antes_day = '0'+str(fecha_antes.day)
        else:
            fecha_antes_day = str(fecha_antes.day)
        if int(fecha_antes.month) < 10:
            fecha_antes_month = '0'+str(fecha_antes.month)
        else:
            fecha_antes_month = str(fecha_antes.month)
        restriccion_fecha_antes = str(fecha_antes.year)+'-'+fecha_antes_month+'-'+fecha_antes_day

        dias_despues = timedelta(days= 1)
        fecha_despues = hoy + dias_despues
        if int(fecha_despues.day) < 10:
            hoy_day = '0'+str(fecha_despues.day)
        else:
            hoy_day = str(fecha_despues.day)
        if int(fecha_despues.month) < 10:
            hoy_month = '0'+str(fecha_despues.month)
        else:
            hoy_month = str(fecha_despues.month)
        restriccion_fecha_despues = str(fecha_despues.year)+'-'+hoy_month+'-'+hoy_day
        widgets = {
             'operador_n': forms.Select(attrs={'class':'form-control', 'disabled':'disabled'}),
             'cite': forms.TextInput(attrs={'class':'form-control', 'onkeyup':'javascript:this.value=this.value.toUpperCase();'}),
             'fecha': forms.TextInput(attrs={'type':'date', 'class':'form-control', 'min':restriccion_fecha_antes}),
             'nombre_ente': forms.TextInput(attrs={'class':'form-control', 'onkeyup':'javascript:this.value=this.value.toUpperCase();'}),
             'representante_ente': forms.TextInput(attrs={'class':'form-control', 'onkeyup':'javascript:this.value=this.value.toUpperCase();'}),
             'cargo_repr': forms.TextInput(attrs={'class':'form-control', 'onkeyup':'javascript:this.value=this.value.toUpperCase();'}),
             'ruta_solicitada': forms.TextInput(attrs={'type':'textarea', 'class':'form-control', 'onkeyup':'javascript:this.value=this.value.toUpperCase();'}),
             'cantidad_tarjetas': forms.TextInput(attrs={'type':'number', 'class':'form-control', 'pattern':'^[0-9]+', 'min':'1'}),
        }
    def clean_cite(self):
        cite = self.cleaned_data.get("cite")
        if cite == None:
            raise forms.ValidationError("Inserte el Numero de Cite")
        return cite
    def clean_nombre_ente(self):
        ente = self.cleaned_data.get("nombre_ente")
        if ente == None:
            raise forms.ValidationError("Inserte el Nombre del ente")
        return ente
    def clean_representante_ente(self):
        repre = self.cleaned_data.get("representante_ente")
        if repre == None:
            raise forms.ValidationError("Introduzca el nombre del representante")
        return repre
    def clean_cargo_repr(self):
        cargo = self.cleaned_data.get("cargo_repr")
        if cargo == None:
            raise forms.ValidationError("Introduzca el cargo del representante")
        return cargo
    def clean_cantidad_tarjetas(self):
        cant = self.cleaned_data.get("cantidad_tarjetas")
        if cant == None:
            raise forms.ValidationError("Introduzca una cantidad solicitada")
        return cant

class FotoVehiculoForm(forms.ModelForm):

    class Meta:
        model = Fotos_Vehiculo
        fields = [
            'vehiculo',
            'foto',
        ]
        labels = {
            'vehiculo': 'Vehiculo',
            'foto': 'Imagen',
        }
        widgets = {
             'vehiculo': forms.Select(attrs={'class':'form-control', 'disabled':'disabled'}),
             'foto': forms.FileInput(attrs={'id':'files', 'name':'files[]'}),
        }

class InformeForm(forms.ModelForm):

    class Meta:
        model = Informe
        fields = [
            'operador',
            'cite',
            'fecha',
            'tipo',
            'anterior',
            'ans_tecnico',
            'concluciones',
        ]
        labels = {
            'cite': 'Nro de Cite',
            'fecha': 'Fecha',
            'tipo': 'Tipo',
            'anterior': 'Observado',
            'ans_tecnico': 'Analisis Tecnico 4to punto',
            'concluciones': 'Conclusiones',
        }
        widgets = {
             'cite': forms.TextInput(attrs={'type':'number', 'class':'form-control', 'pattern':'^[0-9]+', 'min':'1'}),
             'fecha': forms.TextInput(attrs={'type':'date', 'class':'form-control', 'id':'fechaActual', 'readonly':'readonly'}),
             'tipo': forms.Select(choices = (
                                     ('OBSERVADO', ('OBSERVADO')),
                                     ('DEVOLUCION', ('DEVOLUCION')),
                                     ('INFORME TECNICO', ('INFORME TECNICO')),
                                     ), attrs={'class':'form-control'}),
             'ans_tecnico': forms.Textarea(attrs={'placeholder':'Escriba aqui el analisis tecnico', 'class':'form-control', 'rows':'4', 'cols':'50'}),
             'anterior': forms.Select(attrs={'class':'form-control'}),
             'concluciones': forms.Textarea(attrs={'placeholder':'Escriba aqui las conclusiones','class':'form-control', 'rows':'4', 'cols':'50'}),
        }
    def clean_cite(self):
        cite = self.cleaned_data.get("cite")
        if cite == None:
            raise forms.ValidationError("Introduzca el numero de cite")
        return cite

class DocsForm(forms.ModelForm):

    class Meta:
        model = Docs_Legal
        fields = [
            'operador',
            'cite',
            'fecha',
            'numero_ra',
        ]
        labels = {
            'cite': 'Numero',
            'fecha': 'Fecha',
            'numero_ra': 'Numero',
        }
        widgets = {
             'cite': forms.TextInput(attrs={'type':'number', 'class':'form-control', 'pattern':'^[0-9]+', 'min':'1'}),
             'fecha': forms.TextInput(attrs={'type':'date', 'id':'fechaActual', 'class':'form-control', 'readonly':'readonly'}),
             'numero_ra': forms.TextInput(attrs={'type':'number', 'class':'form-control', 'pattern':'^[0-9]+', 'min':'1'}),
        }
    # def clean_cite(self):
    #     cite = self.cleaned_data.get("cite")
    #     if cite == None:
    #         raise forms.ValidationError("Introduzca un valor")
    #     return cite
    # def clean_numero_ra(self):
    #     rs = self.cleaned_data.get("numero_ra")
    #     if rs == None:
    #         raise forms.ValidationError("Introduzca un valor")
    #     return rs

class DocsLegalForm(ModelForm):
    class Meta:
        model = Docs_Legal
        fields = ['descripcion']

class RutaForm(forms.ModelForm):

    class Meta:
        model = Ruta
        fields = [
            'operador',
            'ruta',
            'hora',
        ]
        labels = {
            'ruta': 'Ruta',
            'hora': 'Hora y/o Frecuencia',
        }
        widgets = {
             'ruta': forms.TextInput(attrs={'class':'form-control', 'onkeyup':'javascript:this.value=this.value.toUpperCase();'}),
             'hora': forms.TextInput(attrs={'class':'form-control', 'onkeyup':'javascript:this.value=this.value.toUpperCase();'}),
        }