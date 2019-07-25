# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core import serializers
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.db.models import Q

import os
import qrcode
import json
import time
from datetime import datetime ,date, timedelta
# imports views generics 
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView, DeleteView, View

# imports recorators
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required

# Imports forms from app tranite
from apps.tramite.form import TramiteForm, AsignacionForm
# Imports model from app tranite
from apps.tramite.models import Tramite, Asignar_Vehiculo

# Imports model from app tecnico
from apps.tecnico.models import Operador_Nuevo, Vehiculo_Nuevo, Ruta, Docs_Legal, Checklist_Vehiculo
# Imports model from app operario
from apps.tecnico.models import Razon_Social, Nota, Informe

# Import for PDF documents ReportLab
from django.conf import settings
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.platypus import (SimpleDocTemplate, Spacer, Frame, Paragraph, NextPageTemplate, PageBreak, PageTemplate, Table, TableStyle)
from reportlab.platypus import Image
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm, cm
from reportlab.lib import colors
from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import letter, landscape, portrait
# Create your views here.
from datetime import datetime, date, timedelta

@method_decorator(permission_required('tramite.administrar_tramite'), name='dispatch') 
class CrearTramite(CreateView):
    model = Tramite
    template_name = 'tramite/tramite_form.html'
    form_class = TramiteForm
    def form_valid(self, form):
        self.object = form.save(commit = False)
        # cript for fenecer un tramita al momento de crear uno nuevo
        operador = self.object.solicitante
        tramites = Tramite.objects.filter(solicitante=operador.id, vigente=True)
        if tramites:
            for tramite in tramites:
                tramite.vigente = False
                tramite.save()

        fecha_actual = time.strftime('%Y-%m-%d')
        self.object.fecha_ingreso = fecha_actual
        self.object.hora_ingreso = time.strftime("%H:%M:%S")
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('tramite:listar_tramite'))

def search_operador_nombre(request):
    if request.is_ajax():
        # operadores = Operador_Nuevo.objects.filter( nombre__icontains = request.GET['name']).values('id', 'razon_social', 'nombre')
        operadores = Operador_Nuevo.objects.filter(es_nuevo=False, nombre__icontains = request.GET['name']).values('id', 'nombre')[:10]
        if len(operadores) == 0:
            return HttpResponse(
                json.dumps(
                        [
                            {
                                'id': 'X',
                                'razon_social': '',
                                'nombre': 'No se encontro coincidencias',
                            },
                        ]
                ),
                content_type = 'application/json'
            )
        return HttpResponse(json.dumps(list(operadores)), content_type='application/json')
    else:
        return HttpResponse("Solo Ajax")

# @method_decorator(permission_required('tramite.administrar_tramite', login_url='tramite'), name='dispatch')
@method_decorator(permission_required('tramite.administrar_tramite'), name='dispatch')
class ListarTramite(ListView):
    model = Tramite
    template_name = 'tramite/listar_tramites.html'
    def get_context_data(self, *args, **kwargs):
        context = super(ListarTramite, self).get_context_data(*args, **kwargs)
        
        tramite_ingresado = Tramite.objects.filter(estado='INGRESADO')
        context['tramites_ing'] = tramite_ingresado
        tramite_proceso = Tramite.objects.filter(estado='PROCESO')
        context['tramites_pro'] = tramite_proceso
        tramite_orden_deposito = Tramite.objects.filter(estado='PROCESO' ,tiene_orden=True)
        context['tramite_orden'] = tramite_orden_deposito

        for tramite in tramite_orden_deposito:
            asignados_orden = Asignar_Vehiculo.objects.filter(tramite=tramite.id)
            asignados_con_tarjeta = Asignar_Vehiculo.objects.filter(tramite=tramite.id, tiene_tarjeta= True)
            if not tramite.finalizar:
                if len(asignados_orden) == len(asignados_con_tarjeta):
                    tramite.finalizar = True
                    tramite.save()
        # print('4444444444444444444444 '+ str(len(asignados_orden)))
        # print('4444444444444444444444 '+ str(len(asignados_con_tarjeta)))
        tramite_finalizado = Tramite.objects.filter(estado='ENTREGADO', finalizar=True)
        context['tramite_finalizado'] = tramite_finalizado

        return context

@method_decorator(permission_required('tramite.administrar_tramite'), name='dispatch')
class AsignarVehiculos(DetailView):
    model = Tramite
    template_name = 'tramite/asignar_vehiculos.html'

    def get_context_data(self, *args, **kwargs):
        context = super(AsignarVehiculos, self).get_context_data(*args, **kwargs)
        vehi_asignados = Asignar_Vehiculo.objects.filter(tramite=self.kwargs['pk'])

        context['vehiculos_asignados'] = vehi_asignados
        
        context['form_tramite'] = TramiteForm()

        return context

@method_decorator(permission_required('tramite.administrar_tramite'), name='dispatch')
class AsignarVehiculo(CreateView):
    model = Asignar_Vehiculo
    template_name = 'tramite/asignar_vehiculo.html'
    form_class = AsignacionForm

    def get_initial(self):
        gestion = time.strftime("%Y")
        monto = 40
        return {
            'gestion': gestion,
            'monto': monto,
        }
    
    def get_context_data(self, *args, **kwargs):
        context = super(AsignarVehiculo, self).get_context_data(*args, **kwargs)
        tramite = Tramite.objects.get(id=self.kwargs['pk'])
        context['tramite'] = tramite
        operador = Operador_Nuevo.objects.get(id=tramite.solicitante.id)
        context['operador'] = operador
        return context

    def form_valid(self, form):
        self.object = form.save(commit = False)
        tramite = Tramite.objects.get(id=self.kwargs['pk'])
        self.object.tramite_id = tramite.id
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('tramite:asignar_vehiculos', kwargs = {
            'pk': tramite.id
        }))

@method_decorator(permission_required('tramite.administrar_tramite'), name='dispatch')
class EliminarAsignacion(DeleteView):
    model = Asignar_Vehiculo
    template_name = 'tramite/eliminar_asignacion.html'
    def get_success_url(self, **kwargs):
        return reverse_lazy('tramite:asignar_vehiculos', kwargs = {
            'pk': self.kwargs['fk']})

    def get_context_data(self, *args, **kwargs):
        context = super(EliminarAsignacion, self).get_context_data(*args, **kwargs)
        #Mando la llave fk para el boton de cancelar
        context['llave'] = self.kwargs['fk'];
        return context

class TramiteProceso(UpdateView):
    model = Tramite
    template_name = ''
    form_class = TramiteForm
    def form_valid(self, form):
        tramite = Tramite.objects.get(id=self.object.id)
        tramite.estado = 'PROCESO'
        tramite.save()
        return HttpResponseRedirect(reverse_lazy('tramite:listar_tramite'))

def search_vehiculo_placa(request):
    if request.is_ajax():     
        #Algoritmo para sacar a todos los vehiculos del operador
        id_vehis = []
        vehis = Vehiculo_Nuevo.objects.filter(operador=request.GET['operador'], es_nuevo=False)
        for v in vehis:
            id_vehis.append(v.id)
        print('aaaaaaaaaaaaaa '+str(id_vehis))

        #Algoritmo para sacar el vehiculo que ya esta registrado y que no este caducado
        registrados = []
        regist2 = Asignar_Vehiculo.objects.filter(vehiculo__in=id_vehis, caducado=False)
        # print('aaaaaaaaaaaaaa m '+str(regist2[0].id))
        for ve in regist2:
            registrados.append(ve.vehiculo_id)
        # print('aaaaaaaaaaaaaa d '+str(registrados)) 

        # vehiculosRenovacion = Vehiculo_Nuevo.objects.filter(Q(operador = self.object, renovando=True) | Q(operador = self.object, renovando=False, es_nuevo=True))
        # vehiculos = Vehiculo_Nuevo.objects.filter(operador=request.GET['operador'] , placa__icontains = request.GET['name']).values('id', 'propietario', 'placa')[:10]
        vehiculos = Vehiculo_Nuevo.objects.filter(operador=request.GET['operador'], es_nuevo=False , placa__icontains = request.GET['name']).exclude(id__in=registrados).values('id', 'propietario', 'placa')[:10]
        if len(vehiculos) == 0:
            return HttpResponse(
                json.dumps(
                        [
                            {
                                'id':'',
                                'propietario': '',
                                'placa': 'No se encontro coincidencias',
                            },
                        ]
                ),
                content_type = 'application/json'
            )
        return HttpResponse(json.dumps(list(vehiculos)), content_type='application/json')
    else:
        return HttpResponse("Permitido solo con metodo Ajax")

@method_decorator(permission_required('tramite.administrar_tramite'), name='dispatch')
class ordenDeposito(View):
    def encabezado_pie(self, pdf, document):
        pdf.saveState()
        escudo = settings.MEDIA_ROOT+'/orden/escudo.jpg'
        logo_transporte = settings.MEDIA_ROOT+'/informes/logo_transporte.jpg'
        # Definimos el tamaño de la imagen a cargar y las coordenadas correspondientes
        pdf.drawImage(escudo, 75, 680, 60, 60,preserveAspectRatio=True)
        # Establecemos el tamaño de letra en 10 y el tipo de letra Times-Roman
        pdf.setFont("Times-Roman", 10)
        # Dibujamos una cadena en la ubicación X,Y especificada
        pdf.drawString(165, 720, u"GOBIERNO AUTÓNOMO DEPARTAMENTAL DE POTOSÍ")
        pdf.setFont("Times-Roman", 10)
        pdf.drawString(160, 710, u"UNIDAD DE REGISTRO Y REGULACIÓN DE TRANSPORTE")
        pdf.setFont("Times-Bold", 10.5)
        pdf.drawString(135, 695, u"FORMULARIO DE VERIFICACIÓN DE DATOS - TARJETA INTERPROVINCIAL")

    def vehiculos(self, floables, spacer, styles, tramite):
        styles.add(ParagraphStyle(name = "tramite_bold",  alignment=TA_LEFT, fontSize=12, fontName="Times-Bold"))
        styles.add(ParagraphStyle(name = "orden",  alignment=TA_LEFT, fontSize=12, fontName="Times-Roman"))
        styles.add(ParagraphStyle(name = "orden1",  alignment=TA_LEFT, fontSize=8, fontName="Times-Roman"))
        asignaciones = Asignar_Vehiculo.objects.filter(tramite=tramite.id)
        # print('gggggggggg-------ddddddddd'+ str(asignaciones[0].tramite_id))
        operador = Operador_Nuevo.objects.get(id=tramite.solicitante_id)
        rutas = Ruta.objects.filter(operador=operador.id)
        data = []
        for asignacion in asignaciones:
            vehiculo = Vehiculo_Nuevo.objects.get(id=asignacion.vehiculo_id)
            fila = []
            fila.append(Paragraph('Nro Trámite:', styles['tramite_bold']))
            fila.append(Paragraph(str(tramite.id), styles['orden']))
            data.append(fila)
            fila = []
            fila.append(Paragraph(str('Fecha:'), styles['orden']))
            fila.append(Paragraph(str(tramite.fecha_ingreso), styles['orden']))
            fila.append(Paragraph(str('Hora:'), styles['orden']))
            fila.append(Paragraph(str(tramite.hora_ingreso), styles['orden']))
            data.append(fila)
            fila = []
            fila.append(Paragraph(str('Propietario:'), styles['orden']))
            print('jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj '+'{}'.format(vehiculo.propietario))
            fila.append(Paragraph('{}'.format(vehiculo.propietario), styles['orden']))
            data.append(fila)
            fila = []
            fila.append(Paragraph(str('Empresa:'), styles['orden']))
            fila.append(Paragraph(operador.nombre, styles['orden1']))
            data.append(fila)
            fila = []
            fila.append(Paragraph(str('Placa:'), styles['orden']))
            fila.append(Paragraph(str(vehiculo.placa), styles['orden']))
            fila.append(Paragraph(str('Tipo Transporte:'), styles['orden']))
            fila.append(Paragraph(str(operador.tipo), styles['orden']))
            data.append(fila)
            fila = []
            fila.append(Paragraph(str('Modelo:'), styles['orden']))
            fila.append(Paragraph(str(vehiculo.modelo), styles['orden']))
            fila.append(Paragraph(str('Marca:'), styles['orden']))
            fila.append(Paragraph(str(vehiculo.marca), styles['orden']))
            data.append(fila)
            fila = []
            fila.append(Paragraph(str('Num. Registro:'), styles['orden']))
            fila.append(Paragraph(str(tramite.id), styles['orden']))
            fila.append(Paragraph(str('Chasis:'), styles['orden']))
            fila.append(Paragraph(str(vehiculo.chasis), styles['orden1']))
            data.append(fila)
            fila = []
            fila.append(Paragraph(str('Tipo Servicio:'), styles['orden']))
            fila.append(Paragraph(str(vehiculo.tipo_vehiculo), styles['orden']))
            fila.append(Paragraph(str('Capacidad:'), styles['orden']))
            fila.append(Paragraph(str(vehiculo.capacidad), styles['orden']))
            data.append(fila)
            fila = []
            fila.append(Paragraph(str('Rutas Autorizadas:'), styles['orden']))
            data.append(fila)
            fila = []
            cadena = ''
            for ruta in rutas:
                cadena += ruta.ruta.upper()+' Y VICEVERSA, &nbsp;&nbsp;'
            cadena += '.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-////'
            print('gggggggggg-------ddddddddd'+ cadena)
            fila.append(Paragraph(cadena, styles['orden']))
            data.append(fila)
            fila = []
            fila.append(Paragraph(str('Validez:'), styles['orden']))
            fila.append(Paragraph(str(asignacion.validez)+ ' Año', styles['orden']))
            fila.append(Paragraph(str('Monto:'), styles['orden']))
            fila.append(Paragraph(str(asignacion.monto)+ ' Bs.', styles['orden']))
            data.append(fila)

            tabla = Table(data = data, style = [('BOX',(0,0),(-1,-1),0.5,colors.grey), ('SPAN', (1,3),(3,3)), ('SPAN', (0,8),(3,8)), ('SPAN', (0,9),(3,9)), ('VALIGN', (0,3),(0,3),'MIDDLE')] )
            # tabla = Table(data = data, style = [('BOX',(0,0),(-1,-1),0.5,colors.grey),('SPAN', (1,4),(1,-1))] )
            floables.append(tabla)
            data = []

    
    def instructivo(self, floables, spacer, styles, tramite):
        styles.add(ParagraphStyle(name = "instructivo",  alignment=TA_JUSTIFY, fontSize=12, fontName="Times-Roman"))
        # floables.append(spacer)
        # # como poner una Tabla 
        data = []
        for a in range(1):
            fila = []
            fila.append(Paragraph(u'<strong>Instructivo:</strong>', styles["instructivo"]))
            data.append(fila)
            fila = []
            fila.append(Paragraph(u'<strong>a)</strong> Lea detalladamente los datos de cada uno de los vehículos en el presente formulario.', styles["instructivo"]))
            data.append(fila)
            fila = []
            fila.append(Paragraph(u'<strong>b)</strong> Si encuentra algún error, resaltarlo y devolverlo a la Unidad de Registro y Regulación de Transporte para su corrección sin firmar.', styles["instructivo"]))
            data.append(fila)
            fila = []
            fila.append(Paragraph(u'<strong>c)</strong> Si Todos los datos estan correctos, firmar el formulario y proceder a realizar el deposito correspondiente en la cuenta <strong>N: 1-6024553</strong> del <strong>BANCO UNION</strong> por el total de las terjetas, luego entregar fotocopia del presente formulario y del comprobante de deposito a Tesorería de la Gobernación.', styles["instructivo"]))
            data.append(fila)
        
        tabla = Table(data = data, style = [('BOX',(0,0),(-1,-1),0.5,colors.grey),])
        floables.append(tabla)

    def firmas(self, floables, spacer, styles, tramite):
        styles.add(ParagraphStyle(name = "firmas",  alignment=TA_LEFT, fontSize=7, fontName="courier"))
        styles.add(ParagraphStyle(name = "firmas_r",  alignment=TA_LEFT, fontSize=10, fontName="Times-Roman"))
        # floables.append(spacer)
        data = []
        fila = []
        fila.append(Paragraph(u'&nbsp;&nbsp;<strong>JURO LA EXACTITUD DE LOS DATOS DEL PRESENTE FORMULARIO </strong>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<strong>ACLARACIÓN DE LA FIRMA</strong>', styles["firmas"]))
        data.append(fila)
        fila = []
        fila.append(Paragraph(u'&nbsp;', styles["firmas"]))
        data.append(fila)
        fila = []
        fila.append(Paragraph(u'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Nombre:', styles["firmas_r"]))
        data.append(fila)
        fila = []
        fila.append(Paragraph(u'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;________________________________&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;________________________________', styles["firmas"]))
        data.append(fila)
        fila = []
        fila.append(Paragraph(u'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<strong>Firma Rep. legal</strong> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;C.I.:', styles["firmas_r"]))
        data.append(fila)
        fila = []
        fila.append(Paragraph(u'&nbsp;', styles["firmas"]))
        data.append(fila)
        
        tabla = Table(data = data, style = [('BOX',(0,0),(-1,-1),0.5,colors.grey),])
        floables.append(tabla)
        # # como poner una Tabla 
        
        # for a in range(1):
        #     fila = []
        #     fila.append(Paragraph(u'<strong>Instructivo:</strong>', styles["instructivo"]))
        #     data.append(fila)
        #     fila = []
        #     fila.append(Paragraph(u'<strong>a)</strong> Lea detalladamente los datos de cada uno de los vehículos en el presente formulario.', styles["instructivo"]))
        #     data.append(fila)
        #     fila = []
        #     fila.append(Paragraph(u'<strong>b)</strong> Si encuentra algún error, resaltarlo y devolverlo a la Unidad de Registro y Regulación de Transporte para su corrección sin firmar.', styles["instructivo"]))
        #     data.append(fila)
        #     fila = []
        #     fila.append(Paragraph(u'<strong>c)</strong> Si Todos los datos estan correctos, firmar el formulario y proceder a realizar el deposito correspondiente en la cuenta <strong>N: 1-6024553</strong> del <strong>BANCO UNION</strong> por el total de las terjetas, luego entregar fotocopia del presente formulario y del comprobante de deposito a Tesorería de la Gobernación.', styles["instructivo"]))
        #     data.append(fila)
        
        # tabla = Table(data = data, style = [('BOX',(0,0),(-1,-1),0.5,colors.grey),])
        # floables.append(tabla)

    def get(self, request, *args, **kwargs):
        #Indicamos el tipo de contenido a devolver, en este caso un pdf
        response = HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename="First-PDF.pdf"'
        #La clase io.BytesIO permite tratar un array de bytes como un fichero binario, se utiliza como almacenamiento temporal
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize = letter,
                                rightMargin = 60,
                                leftMargin = 80,
                                topMargin = 115,
                                bottomMagin= 48,
                                showBoundary = True
                                )
        styles = getSampleStyleSheet()
        flowables = []
        spacer = Spacer(1, 0.25*inch)
        # Obtener el trámite
        tramite = Tramite.objects.get(id=self.kwargs['pk'], estado='PROCESO')
        self.vehiculos(flowables, spacer, styles, tramite)
        self.instructivo(flowables, spacer, styles, tramite)
        self.firmas(flowables, spacer, styles, tramite)

        doc.build(flowables, onFirstPage=self.encabezado_pie, onLaterPages=self.encabezado_pie)
        response.write(buffer.getvalue())
        buffer.close()
        
        tramite.tiene_orden = True
        tramite.save()
        return response

@method_decorator(permission_required('tramite.administrar_tramite'), name='dispatch')
class ListarTarjetas(ListView):
    model = Asignar_Vehiculo
    template_name = 'tramite/listar_tarjetas.html'
    def get_context_data(self, *args, **kwargs):
        context = super(ListarTarjetas, self).get_context_data(*args, **kwargs)
        
        asignados = Asignar_Vehiculo.objects.filter(tramite=self.kwargs['pk'])
        context['asignados'] = asignados

        return context

import datetime
@method_decorator(permission_required('tramite.administrar_tramite'), name='dispatch')
class Tarjetas(View):
    def encabezado_pie(self, pdf, document):
        pdf.saveState()
        # Establecemos el tamaño de letra en 10 y el tipo de letra Times-Roman
        pdf.setFont("Helvetica", 6.5)
        # Dibujamos una cadena en la ubicación X,Y especificada
        pdf.drawString(140, 335, u"LICENCIA DE OPERACION PARA EL AUTOTRANSPORTE")
        
        asignado = Asignar_Vehiculo.objects.get(id=self.kwargs['pk'])
        tramite = Tramite.objects.get(id=asignado.tramite_id)
        operador = Operador_Nuevo.objects.get(id=tramite.solicitante_id)
        razon_social = Razon_Social.objects.get(id=operador.razon_social_id)
        print('==========='+str(razon_social))
        if razon_social.id == 2:
            pdf.drawString(165, 328, u"AUTOMOTOR INTERPROVINCIAL - ATL")
        elif razon_social == 3:
            pdf.drawString(148, 328, u"AUTOMOTOR INTERPROVINCIAL - COOPERATIVAS")
        else:
            pdf.drawString(175, 328, u"AUTOMOTOR INTERPROVINCIAL")

        pdf.setFont("Times-Italic", 6.5)
        pdf.drawString(70, 40, u"Abg. Wilson Condori López")
        pdf.drawString(230, 40, u"Dr. Juan Carlos Cejas Ugarte")
        pdf.drawString(390, 40, u"Abg. Daniel Antonio Apaza Barrera")

        pdf.setFont("Times-Italic", 6.5)
        pdf.drawString(50, 33, u"RESPONSABLE UNIDAD DE REGISTRO Y")
        pdf.drawString(240, 33, u"GOBERNADOR DEL")
        pdf.drawString(380, 33, u"DIRECTOR JURIDICO DEPARTAMENTAL")
        
        pdf.drawString(60, 26, u"REGULACION DE TRANSPORTE")
        pdf.drawString(220, 26, u"DEPARTAMENTO AUTONOMO DE")

        pdf.drawString(255, 19, u"POTOSI")

    def tarjeta(self, floables, spacer, styles, asignado):
        styles.add(ParagraphStyle(name = "tramite_bold",  alignment=TA_LEFT, fontSize=10, fontName="Helvetica-Bold"))
        styles.add(ParagraphStyle(name = "tramite_bold1",  alignment=TA_LEFT, fontSize=8, fontName="Helvetica-Bold"))
        styles.add(ParagraphStyle(name = "title_1",  alignment=TA_CENTER, fontSize=6.5, fontName="Helvetica"))
        styles.add(ParagraphStyle(name = "title_2",  alignment=TA_CENTER, fontSize=6.5, fontName="Times-Italic"))
        styles.add(ParagraphStyle(name = "orden",  alignment=TA_LEFT, fontSize=10, fontName="Helvetica"))
        styles.add(ParagraphStyle(name = "orden1",  alignment=TA_LEFT, fontSize=8, fontName="Helvetica"))
        styles.add(ParagraphStyle(name = "rutas",  alignment=TA_LEFT, fontSize=6, fontName="Helvetica"))
        styles.add(ParagraphStyle(name = "orden_right",  alignment=TA_RIGHT, fontSize=8, fontName="Helvetica"))
        styles.add(ParagraphStyle(name = "placa",  alignment=TA_CENTER, fontSize=13, fontName="Helvetica-Bold"))
        # asignaciones = Asignar_Vehiculo.objects.filter(tramite=tramite.id)
        # print('gggggggggg-------ddddddddd'+ str(asignaciones[0].tramite_id))
        tramite = Tramite.objects.get(id=asignado.tramite_id)
        operador = Operador_Nuevo.objects.get(id=tramite.solicitante_id)
        vehiculo = Vehiculo_Nuevo.objects.get(id=asignado.vehiculo_id)
        rutas = Ruta.objects.filter(operador=operador.id)
        
        text = 'LICENCIA DE OPERACIONES PARA EL AUTOTRANSPORTE'
        para = Paragraph(text, styles["title_1"])
        floables.append(para)

        razon_social = Razon_Social.objects.get(id=operador.razon_social_id)
        if razon_social.id == 2:
            text = 'AUTOMOTOR INTERPROVINCIAL - ATL'
            para = Paragraph(text, styles["title_1"])
            floables.append(para)
            floables.append(spacer)
        elif razon_social == 3:
            text = 'AUTOMOTOR INTERPROVINCIAL - COOPERATIVAS'
            para = Paragraph(text, styles["title_1"])
            floables.append(para)
            floables.append(spacer)
        else:
            text = 'AUTOMOTOR INTERPROVINCIAL'
            para = Paragraph(text, styles["title_1"])
            floables.append(para)
            floables.append(spacer)

        data = []
        fila = []
        fila.append(Paragraph('OPERADOR:', styles['tramite_bold']))
        fila.append(Paragraph(operador.nombre.upper(), styles['tramite_bold1']))
        data.append(fila)
        fila = []
        fila.append(Paragraph('PROPIETARIO:', styles['tramite_bold']))
        fila.append(Paragraph('{}'.format(vehiculo.propietario), styles['orden1']))
        fila.append(Paragraph('', styles['orden']))
        fila.append(Paragraph('', styles['orden']))
        mensaje = 'OPERADOR: {}'.format(operador.nombre)+'\n'
        mensaje+= 'PLACA DEL VEHICULO: {}'.format(vehiculo.placa)+'\n'
        mensaje+= 'PROPIETARIO: {}'.format(vehiculo.propietario)+'\n'
        mensaje+= 'MARCA: {}'.format(vehiculo.marca)+'\n'
        mensaje+= 'VALIDEZ: DEL {} AL {}'.format(asignado.valida_del, asignado.valida_al)+'\n'

        qr = qrcode.QRCode(
            version = 1,
            error_correction = qrcode.constants.ERROR_CORRECT_L,
            box_size = 10,
            border = 4,
        )
        qr.add_data(mensaje)
        qr.make(fit = True)
        img = qr.make_image()
        f = open(settings.MEDIA_ROOT + '/qrcodes/qr-' + str(vehiculo.placa) + '.png', "wb")
        img.save(f)
        f.close()
        # img = qrcode.make('PLACA:{}'.format(vehiculo.placa))
        # img.save('qr.png')
        img_qr = settings.MEDIA_ROOT + '/qrcodes/qr-' + str(vehiculo.placa) + '.png'
        f = Image(img_qr,80,80)
        fila.append(f) 
        data.append(fila)
        fila = []
        fila.append(Paragraph('MODELO:', styles['tramite_bold']))
        fila.append(Paragraph(str(vehiculo.modelo), styles['orden']))
        fila.append(Paragraph('CAPACIDAD:', styles['tramite_bold']))
        fila.append(Paragraph(str(vehiculo.capacidad), styles['orden']))
        fila.append(Paragraph('', styles['orden']))
        data.append(fila)
        fila = []
        fila.append(Paragraph('REGISTRO:', styles['tramite_bold']))
        fila.append(Paragraph(str(tramite.id), styles['orden']))
        fila.append(Paragraph('CHASIS:', styles['tramite_bold']))
        fila.append(Paragraph(str(vehiculo.chasis), styles['orden1']))
        fila.append(Paragraph('', styles['orden']))
        data.append(fila)
        fila = []
        fila.append(Paragraph('CATEGORIA:', styles['tramite_bold']))
        fila.append(Paragraph(str(operador.tipo), styles['orden']))
        fila.append(Paragraph('MARCA:', styles['tramite_bold']))
        fila.append(Paragraph(str(vehiculo.marca), styles['orden']))
        fila.append(Paragraph('', styles['orden']))
        data.append(fila)
        fila = []
        fila.append(Paragraph('', styles['orden']))
        fila.append(Paragraph('', styles['orden']))
        fila.append(Paragraph('', styles['orden']))
        fila.append(Paragraph('', styles['orden']))
        fila.append(Paragraph('', styles['orden']))
        data.append(fila)
        fila = []
        fila.append(Paragraph('', styles['orden']))
        fila.append(Paragraph('', styles['orden']))
        fila.append(Paragraph('', styles['orden']))
        fila.append(Paragraph('', styles['orden']))
        fila.append(Paragraph(str(vehiculo.placa), styles['placa']))
        data.append(fila)
        fila = []
        # fila.append(Paragraph('RUTAS AUTORIZADAS:', styles['tramite_bold']))
        fila.append(Paragraph('', styles['tramite_bold']))
        fila.append(Paragraph('', styles['orden']))
        fila.append(Paragraph('', styles['orden']))
        fila.append(Paragraph('', styles['orden']))
        fila.append(Paragraph('', styles['orden']))
        data.append(fila)
        fila = []
        cadena = ''
        for ruta in rutas:
            cadena += ruta.ruta.upper()+' Y VICEVERSA.-.-'
        cadena += '.-////'
        # fila.append(Paragraph(cadena, styles['rutas']))
        fila.append(Paragraph('', styles['rutas']))
        fila.append(Paragraph('', styles['orden']))
        fila.append(Paragraph('', styles['orden']))
        fila.append(Paragraph('', styles['orden']))
        fila.append(Paragraph('', styles['orden']))
        data.append(fila)
        fila = []
        fila.append(Paragraph('<strong>LICENCIA VALIDA DE:&nbsp;&nbsp;</strong> {} <strong>&nbsp;&nbsp;AL:</strong>&nbsp;&nbsp; {}'.format(asignado.valida_del, asignado.valida_al), styles['orden']))
        fila.append(Paragraph('', styles['orden']))
        fila.append(Paragraph('', styles['orden']))
        fila.append(Paragraph('', styles['orden']))
        fila.append(Paragraph('', styles['orden']))
        data.append(fila)

        hoy = asignado.valida_del
        print('1111111111111111111111111'+str(hoy))
        # hoy = datetime.date.today()
        dia = datetime.date.weekday(hoy)
        dias = ["Lunes",
                "Martes",
                "Miercoles",
                "Jueves",
                "Viernes",
                u"Sábado",
                "Domingo"]
        meses = ["Enero",
                "Febrero",
                "Marzo",
                "Abril",
                "Mayo",
                "Junio",
                "Julio",
                "Agosto",
                "Septiembre",
                "Octubre",
                "Noviembre",
                "Diciembre"]
        dia_l = dias[dia]
        mes_l = meses[hoy.month-1]
        # hoy = hoy + timedelta(days=1) #Sumar un dia a la fecha
        # dia_sem = datetime.date.weekday(hoy) # optiene un numero del 0 al 6 del dia de la semana lunel =0
        fecha_l = u"Potosí-{}, {} de {} de {}".format(dia_l, hoy.day, mes_l, hoy.year)
        print('ddddddddddd---------------'+ fecha_l)
        fila = []
        fila.append(Paragraph(fecha_l , styles['orden_right']))
        fila.append(Paragraph('', styles['orden']))
        fila.append(Paragraph('', styles['orden']))
        fila.append(Paragraph('', styles['orden']))
        fila.append(Paragraph('', styles['orden']))
        data.append(fila)
        # tabla = Table(data = data, style = [('BOX',(0,0),(-1,-1),0.5,colors.grey), ('SPAN', (1,3),(3,3)), ('SPAN', (0,8),(3,8)), ('SPAN', (0,9),(3,9)), ('VALIGN', (0,3),(0,3),'MIDDLE')] )
        # tabla = Table(data = data, colWidths=[5 for x in range(1,6)], rowHeights=[5 for x in range(len(data))])
        tabla = Table(data = data)
        tabla.setStyle(TableStyle([
                                    ('SPAN',(1,0),(4,0)),
                                    ('SPAN',(1,1),(3,1)),
                                    ('SPAN',(0,7),(4,7)),
                                    ('SPAN',(0,8),(4,8)),
                                    ('SPAN',(0,9),(4,9)),
                                    ('SPAN',(0,10),(4,10)),
                                    ('SPAN',(4,1),(4,5)),
                                    ('LINEABOVE',(4,6),(4,6),1.0,colors.black),
                                    ('LINEAFTER',(4,6),(4,6),1.0,colors.black),
                                    ('LINEBEFORE',(4,6),(4,6),1.0,colors.black),
                                    ('LINEBELOW',(4,6),(4,6),1.0,colors.black),
                                    ]
                                )
                        )
        floables.append(tabla)
        floables.append(spacer)
        floables.append(spacer)
        floables.append(spacer)
        floables.append(spacer)

        data = []
        fila = []
        fila.append(Paragraph('Abg. Wilson Condori Lopez', styles['title_2']))
        fila.append(Paragraph('Dr. Juan Carlos Cejas Ugarte', styles['title_2']))
        fila.append(Paragraph('Abg. Daniel Antonio Apaza Barrera', styles['title_2']))
        data.append(fila)
        fila = []
        fila.append(Paragraph('RESPONSABLE UNIDAD DE REGISTRO Y', styles['title_2']))
        fila.append(Paragraph('GOBERNADOR DEL', styles['title_2']))
        fila.append(Paragraph('DIRECTOR JURIDICO DEPARTAMENTAL', styles['title_2']))
        data.append(fila)
        fila = []
        fila.append(Paragraph('REGULACION DE TRANSPORTE', styles['title_2']))
        fila.append(Paragraph('DEPARTAMENTO AUTONOMO DE', styles['title_2']))
        fila.append(Paragraph('', styles['title_2']))
        data.append(fila)
        fila = []
        fila.append(Paragraph('', styles['title_2']))
        fila.append(Paragraph('POTOSI', styles['title_2']))
        fila.append(Paragraph('', styles['title_2']))
        data.append(fila)

        tabla = Table(data = data, colWidths=[150 for x in range(3)],
                        rowHeights=[6 for x in range(len(data))])
        tabla.setStyle(TableStyle([]
                                )
                        )
        floables.append(tabla)
        floables.append(spacer)
        text = 'RUTAS AUTORIZADAS:'
        para = Paragraph(text, styles["tramite_bold"])
        floables.append(para)
        floables.append(Spacer(1, 0.05*inch))

        data = []
        fila = []
        for ruta in rutas:
            fila = []
            fila.append(Paragraph(ruta.ruta.upper(), styles['title_2']))
            fila.append(Paragraph(ruta.hora.upper(), styles['title_2']))
            data.append(fila)

        tabla = Table(data = data, colWidths=[175 for x in range(2)],
                        rowHeights=[15 for x in range(len(data))])
        tabla.setStyle(TableStyle([
            ('GRID',(0,0),(-1,-1),0.5,colors.black),
            ('VALIGN', (0,0),(-1,-1), 'MIDDLE'),
            ]))
        floables.append(tabla)

    
    def get(self, request, *args, **kwargs):
        asignado = Asignar_Vehiculo.objects.get(id=self.kwargs['pk'])
        if not asignado.tiene_tarjeta:
            # hoy = datetime.now().date()
            hoy = datetime.date.today()
            asignado.valida_del = hoy
            # dias = timedelta(days=366)
            # newdate = hoy + dias
            newdate = datetime.date(hoy.year+1, hoy.month, hoy.day)
            asignado.valida_al = newdate
            asignado.tiene_tarjeta = True
            asignado.save()
        #Indicamos el tipo de contenido a devolver, en este caso un pdf
        response = HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename="First-PDF.pdf"'
        #La clase io.BytesIO permite tratar un array de bytes como un fichero binario, se utiliza como almacenamiento temporal
        buffer = BytesIO()
        
        tam_tarjeta = (19*cm,15*cm)
        doc = SimpleDocTemplate(buffer, pagesize= (tam_tarjeta),
                                        rightMargin = 35,
                                        leftMargin = 35,
                                        topMargin = 75,
                                        bottomMargin= 17,
                                        showBoundary = False
                                )
        styles = getSampleStyleSheet()
        flowables = []
        spacer = Spacer(1, 0.25*inch)
        # Obtener el trámite
 
        self.tarjeta(flowables, spacer, styles, asignado)
        # doc.build(flowables, onFirstPage=self.encabezado_pie, onLaterPages=self.encabezado_pie)
        doc.build(flowables)
        response.write(buffer.getvalue())
        buffer.close()
        vehiculo = Vehiculo_Nuevo.objects.get(id=asignado.vehiculo_id)
        os.remove(settings.MEDIA_ROOT + '/qrcodes/qr-' + str(vehiculo.placa) + '.png')

        return response

class TramiteFinalizar(UpdateView):
    model = Tramite
    template_name = ''
    form_class = TramiteForm
    def form_valid(self, form):
        tramite = Tramite.objects.get(id=self.object.id)
        tramite.estado = 'ENTREGADO'
        tramite.finalizado = True
        tramite.save()
        operador = Operador_Nuevo.objects.get(id=tramite.solicitante_id)
        operador.en_tramite = False
        operador.renovando = False
        operador.save()
        #Poniendo Nota como fenecido para hacer una nueva renovacion a lo posterior
        nota = Nota.objects.get(operador_n= operador.id, fenecio= False)
        nota.fenecio= True
        nota.save()
        #Poniendo a los check actuales como fenecidos para hacer una nueva renovacion a lo posterior
        vehiculos = Vehiculo_Nuevo.objects.filter(operador=operador.id)
        for vehiculo in vehiculos:
            checklists = Checklist_Vehiculo.objects.filter(vigente=True)
            for checklist in checklists:
                check = Checklist_Vehiculo.objects.get(id=checklist.id)
                check.vigente = False
                check.save()
        #Poniendo a los informes como fenecidos para hacer una nueva renovacion a lo posterior
        informes = Informe.objects.filter(operador=operador.id)
        for informe in informes:
            inf = Informe.objects.get(id=informe.id)
            inf.vigente=False
            inf.save()
        #Poniendo a los documentos legales como fenecidos para hacer una nueva renovacion a lo posterior
        docs_legal = Docs_Legal.objects.filter(operador=operador.id, vigente=True)
        for doc in docs_legal:
            d = Docs_Legal.objects.get(id=doc.id)
            d.vigente=False
            d.save()

        #Poniendo a los vehiculos, su campo renovacion en Falso para otra posterior renovacion
        vehiculos_renovando = Vehiculo_Nuevo.objects.filter(operador=operador.id, renovando=True)
        for vehiculo in vehiculos_renovando:
            v = Vehiculo_Nuevo.objects.get(id=vehiculo.id)
            v.renovando=False
            v.save()
        #Poniendo a los vehiculos, su campo en tramite en Falso para otra posterior renovacion
        vehiculos_n = Vehiculo_Nuevo.objects.filter(operador=operador.id, en_tramite=True)
        for vehiculo in vehiculos_n:
            v = Vehiculo_Nuevo.objects.get(id=vehiculo.id)
            v.en_tramite=False
            v.save()

        return HttpResponseRedirect(reverse_lazy('tramite:listar_tramite'))

class ListarSeguimiento(ListView):
    model = Operador_Nuevo
    template_name = 'tramite/listar_seguimiento.html'
    def get_context_data(self, *args, **kwargs):
        context = super(ListarSeguimiento, self).get_context_data(*args, **kwargs)        
        operadores_tramite = Operador_Nuevo.objects.filter(en_tramite=True)
        context['operadores'] = operadores_tramite
        return context

class Seguimiento(DetailView):
    model = Operador_Nuevo
    template_name = 'tramite/seguimiento.html'
    def get_context_data(self, *args, **kwargs):
        context = super(Seguimiento, self).get_context_data(*args, **kwargs)
        operador = Operador_Nuevo.objects.get(id=self.kwargs['pk'])
        context['operador'] = operador
        # seguimiento para tramite ingresado, cuando se registra la nota
        if Nota.objects.filter(operador_n= operador, fenecio= False).exists():
            ingresado = Nota.objects.filter(operador_n= operador, fenecio= False)
            context['ingresado'] = ingresado
        # seguimiento para tramite en verificacion, cuando todos los vehiculos se verificaron
        vehiculos = Vehiculo_Nuevo.objects.filter(Q(operador=operador.id, en_tramite=True) | Q(operador=operador.id, renovando=True))
        cantidad = vehiculos.count()
        contador = 0
        for vehiculo in vehiculos:
            if Checklist_Vehiculo.objects.filter(vehiculo_nuevo=vehiculo, vigente=True).exists():
                contador = contador + 1
        if cantidad != 0:
            if contador == cantidad:
                context['verificado'] = True
        # seguimiento para tramite emitir informes, cuando se emite algun informe
        if Informe.objects.filter(operador= operador, vigente= True).exists():
            informe = Informe.objects.filter(operador= operador, vigente= True)
            context['Informe'] = informe
        # seguimiento para tramite emitir documentos legales, cuando se emite algun documento
        if Docs_Legal.objects.filter(operador= operador, vigente= True).exists():
            doc = Docs_Legal.objects.filter(operador= operador, vigente= True)
            context['doc'] = doc
        # seguimiento para tramite iniciado, cuando se registra el trámite
        if Tramite.objects.filter(solicitante= operador, finalizado= False).exists():
            tramite_inicio = Tramite.objects.filter(solicitante= operador, finalizado= False)
            context['tramite_inicio'] = tramite_inicio
        # seguimiento para tramite proceso, cuando el trámite esta en proceso y se emitio la orden de deposito
        if Tramite.objects.filter(solicitante= operador, finalizado= False, tiene_orden=True).exists():
            tramite_proceso = Tramite.objects.filter(solicitante= operador, finalizado= False, tiene_orden=True)
            context['tramite_proceso'] = tramite_proceso
        # seguimiento para tramite con tarjetas, cuando se imprimen todas las tarjetas del tramite
        if Tramite.objects.filter(solicitante= operador, finalizar= True, finalizado=False).count() == 1:
            tramite_inicio = Tramite.objects.get(solicitante= operador, finalizar= True, finalizado=False)
            cantidad_tarjetas = Asignar_Vehiculo.objects.filter(tramite= tramite_inicio)
            tarjetas_impresas = Asignar_Vehiculo.objects.filter(Q(tramite= tramite_inicio, tiene_tarjeta=True))
            cantidad = cantidad_tarjetas.count()
            impresas = tarjetas_impresas.count()
            if cantidad != 0:
                if impresas == cantidad:
                    context['tarjetas_impresas'] = True
        # seguimiento para tramite finalizado, cuando el trámite ha finalizado
        # if Tramite.objects.filter(solicitante= operador, vigente= True, tiene_orden=True).exists():
        #     tramite_proceso = Tramite.objects.filter(solicitante= operador, vigente= True, tiene_orden=True)
        #     context['tramite_proceso'] = tramite_proceso

        return context

