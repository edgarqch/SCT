# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View
from django.http import HttpResponseRedirect
from django.db.models import Q
from datetime import datetime
import json
from xhtml2pdf import pisa

# imports recorators
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required


# Import your forms here.
from apps.tecnico.form import OperarioNuevoForm, OperarioRenovarForm , VehiculoNForm, VehiculoForm,\
VehiculoRenovForm, NotaForm, FotoVehiculoForm, InformeForm, DocsLegalForm, DocsForm, MarcaForm

# Import your models here.
from apps.tecnico.models import Operador_Nuevo, Vehiculo_Nuevo, Tipo_Vehiculo, Checklist_Operario,\
requisitos_vehiculo_tipo, Requisitos_Vehi, Checklist_Vehiculo, Nota, Fotos_Vehiculo, Informe, Docs_Legal,\
Ruta, Marca
from apps.operario.models import Requisitos_RS, requisitos_razon_social, Razon_Social

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
from reportlab.lib.pagesizes import letter


# Create your views here.
#views for Nota
@method_decorator(permission_required('tecnico.verificar'), name='dispatch') 
class NotaCreate(CreateView):
    model = Nota
    template_name = 'tecnico/nota_form.html'
    form_class = NotaForm
    def form_valid(self, form):
        self.object = form.save(commit = False)
        operador = Operador_Nuevo.objects.get(id=self.kwargs['pk'])
        self.object.operador_n = operador
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('tecnico:operario_detalle', kwargs = {
            'pk': self.object.operador_n.id
        }))

@method_decorator(permission_required('tecnico.verificar'), name='dispatch')
class NotaEdit(UpdateView):
    model = Nota
    template_name = 'tecnico/nota_form.html'
    form_class = NotaForm

    def form_valid(self, form):
        operador = Operador_Nuevo.objects.get(id=self.kwargs['fk'])
        print('-------------'+ str(operador))
        self.object = form.save(commit = False)
        self.object.operador_n = operador
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('tecnico:operario_nuevo_listar'))

# Views for verify Operador nuevo
@method_decorator(permission_required('tecnico.verificar'), name='dispatch') 
class OperarioNuevoCreate(CreateView):
    model = Operador_Nuevo
    template_name = 'tecnico/operario_nuevo_form.html'
    form_class = OperarioNuevoForm
    success_url = reverse_lazy('tecnico:operario_nuevo_listar')
    # def form_valid(self, form):
    #     self.object = form.save(commit = False)
    #     print form.cleaned_data
    #     form_data = form.cleaned_data
    #     print form_data.get('nombre')
    #     name = form_data.get('nombre')
    #     if name:
    #         # obj = Operador_Nuevo.objects.create(nombre=name)
    #         self.object.save()
    #         return HttpResponseRedirect(reverse_lazy('tecnico:operario_nuevo_listar'))
    #     else:
    #         raise form.ValidationError(
    #                 "Did not send for 'help' in the subject despite "
    #                 "CC'ing yourself."
    #             )
    
@method_decorator(permission_required('tecnico.verificar'), name='dispatch') 
class ListarOperarioN(ListView):
    model = Operador_Nuevo
    template_name = 'tecnico/operario_nuevo_listar.html'
    
    def get_context_data(self, *args, **kwargs):
        context = super(ListarOperarioN, self).get_context_data(*args, **kwargs)
        operador_n = Operador_Nuevo.objects.filter(
            Q(vigente= True,es_nuevo= True,en_tramite= True)
            )
        context['operador_n'] = operador_n

        # Algoritmo para determinar si el operador esta listo para ser verificado.
        list_id = []
        for op in operador_n:
            if Vehiculo_Nuevo.objects.filter(operador=op.id).exists() and Nota.objects.filter(operador_n=op.id).exists():
                list_id.append(op.id)
        operador_v = Operador_Nuevo.objects.filter(id__in=list_id, es_nuevo=True)
        context['operador_v'] = operador_v

        # Algoritmo para determinar si el operador ha sido verificado
        list_verifi = []
        for op in operador_v:
            if Checklist_Operario.objects.filter(operador_nuevo=op.id).exists():
                list_verifi.append(op.id)
        operador_inf = Operador_Nuevo.objects.filter(es_nuevo=True, id__in=list_verifi)
        context['operador_inf'] = operador_inf

        return context

@method_decorator(permission_required('tecnico.verificar'), name='dispatch') 
class VerificarOperarioN(ListView):
    model = Operador_Nuevo
    template_name = 'tecnico/operario_nuevo_verificar.html'
    # template_name = 'tecnico/operario_nuevo_listar.html'

    def get_queryset(self):
        queryset = super(VerificarOperarioN, self).get_queryset()
        return queryset.filter(vigente=True)

@method_decorator(permission_required('tecnico.verificar'), name='dispatch') 
class OperarioNuevoDetail(DetailView):
    model = Operador_Nuevo
 
    template_name = 'tecnico/operario_detalle.html'
    def get_context_data(self, *args, **kwargs):
        context = super(OperarioNuevoDetail, self).get_context_data(*args, **kwargs)
        queryset_vehiculo = Vehiculo_Nuevo.objects.filter(operador_id = self.kwargs['pk'])
        queryset_requisitos = requisitos_razon_social.objects.filter(razon_social= self.object.razon_social)

        list_ids = []
        for a in queryset_requisitos:
            list_ids.append(a.requisitos_rs.id)
        queryset_requisitos = Requisitos_RS.objects.filter(id__in=list_ids)
        
        context['lista'] = queryset_vehiculo
        # print ('//////////' + str(queryset_requisitos))
        context['requisitos'] = queryset_requisitos
        context['formulario'] = FotoVehiculoForm()
        contar_vehi = Nota.objects.get(operador_n= self.kwargs['pk'])
        try:
            cont = contar_vehi.cantidad_tarjetas
        except:
            cont = 10
        print('-----------jjjjjjjjjjj'+str(cont))
        vehiculos_registrados = Vehiculo_Nuevo.objects.filter(operador_id = self.kwargs['pk'])
        print ('//////////' + str(len(vehiculos_registrados)))
        if cont == len(vehiculos_registrados):
            prueba = False
        else:
            prueba = True
        context['prueba'] = prueba
        return context

@method_decorator(permission_required('tecnico.verificar'), name='dispatch') 
class VerificarOperario(DetailView):
    model = Operador_Nuevo
    template_name = 'tecnico/operario_verificar.html'
    def get_context_data(self, *args, **kwargs):
        context = super(VerificarOperario, self).get_context_data(*args, **kwargs)
        queryset_requisitos = requisitos_razon_social.objects.filter(razon_social= self.object.razon_social).order_by('id')
        print ('//////////' + str(queryset_requisitos[0].requisitos_rs.id))
        #Algoritmo para crear la verificacion del operador por primera vez
        lista = []
        for a in queryset_requisitos:
            lista.append(a.requisitos_rs.id)
            print ('//////////------' + str(lista))
        requisitos = Requisitos_RS.objects.filter(id__in=lista)
        print ('//////////' + str(requisitos))
        if not Checklist_Operario.objects.filter(operador_nuevo=self.object).exists():    
            for b in requisitos:
                p = Checklist_Operario.objects.create(requisitos=b, operador_nuevo=self.object)
        context['checklists'] = Checklist_Operario.objects.filter(operador_nuevo=self.object)

        vehiculosOp = Vehiculo_Nuevo.objects.filter(operador = self.object)
        context['vehiculosOp'] = vehiculosOp
        return context

#Views for vehiculo
@method_decorator(permission_required('tecnico.verificar'), name='dispatch') 
class CrearVehiculoN(CreateView):
    model = Vehiculo_Nuevo
    template_name = 'tecnico/vehiculo_nuevo_form.html'
    form_class = VehiculoNForm
    
    def form_valid(self, form):
        self.object = form.save(commit = False)
        operador = Operador_Nuevo.objects.get(id=self.kwargs['pk'])
        self.object.operador = operador
        tipo = Tipo_Vehiculo.objects.get(id=1)
        self.object.tipo = tipo
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('tecnico:operario_detalle', kwargs = {
            'pk': self.object.operador.id
        }))

    def get_initial(self):
        tipo = 1
        operario = self.kwargs['pk']
        return {
            'tipo': tipo,
            'operario': operario,
        }
    
    def get_context_data(self, *args, **kwargs):
        context = super(CrearVehiculoN, self).get_context_data(*args, **kwargs)
        operador = Operador_Nuevo.objects.get(id=self.kwargs['pk'])
        pk = operador.id
        context['llave'] = pk
        return context

@method_decorator(permission_required('tecnico.verificar'), name='dispatch') 
class EditarVehiculoN(UpdateView):
    model = Vehiculo_Nuevo
    template_name = 'tecnico/vehiculo_nuevo_form.html'
    form_class = VehiculoForm

    def form_valid(self, form):
        self.object = form.save(commit = False)
        print ('//////////' + str(self.kwargs['fk']))
        print ('//////////' + str(self.kwargs['pk']))
        operador = Operador_Nuevo.objects.get(id=self.kwargs['fk'])
        self.object.operador = operador
        tipo = Tipo_Vehiculo.objects.get(id=1)
        self.object.tipo = tipo
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('tecnico:operario_detalle', kwargs = {
            'pk': operador.id
        }))

    def get_context_data(self, *args, **kwargs):
        context = super(EditarVehiculoN, self).get_context_data(*args, **kwargs)
        context['llave'] = self.kwargs['fk'];
        return context

@method_decorator(permission_required('tecnico.verificar'), name='dispatch') 
class EliminarVehivuloN(DeleteView):
    model = Vehiculo_Nuevo
    template_name = 'tecnico/vehiculo_nuevo_eliminar.html'
    def get_success_url(self, **kwargs):
        return reverse_lazy('tecnico:operario_detalle', kwargs = {
            'pk': self.kwargs['fk']})

    def get_context_data(self, *args, **kwargs):
        context = super(EliminarVehivuloN, self).get_context_data(*args, **kwargs)
        context['llave'] = self.kwargs['fk'];
        return context

@method_decorator(permission_required('tecnico.verificar'), name='dispatch') 
class VerificarVehiculo(DetailView):
    model = Vehiculo_Nuevo
    template_name = 'tecnico/vehiculo_verificar.html'
    def get_context_data(self, *args, **kwargs):
        context = super(VerificarVehiculo, self).get_context_data(*args, **kwargs)
        requisitos_tipo = requisitos_vehiculo_tipo.objects.filter(tipo_vehiculo = self.object.tipo).order_by('id')
        lista = []
        for a in requisitos_tipo:
            lista.append(a.requisitos_vehi.id)
        # print ('/***********' + str(lista))
        requisitos_v = Requisitos_Vehi.objects.filter(id__in = lista)
        if not Checklist_Vehiculo.objects.filter(vehiculo_nuevo=self.object).exists():    
            for b in requisitos_v:
                p = Checklist_Vehiculo.objects.create(requisitos=b, vehiculo_nuevo=self.object)
        context['checklistvehiculos'] = Checklist_Vehiculo.objects.filter(vehiculo_nuevo= self.object)
        return context

class CreateFoto(CreateView):
    model = Fotos_Vehiculo
    template_name = ''
    form_class = FotoVehiculoForm
    def form_valid(self, form):
        self.object = form.save(commit = False)
        vehiculo = Vehiculo_Nuevo.objects.get(id=self.kwargs['pk'])
        self.object.vehiculo = vehiculo
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('tecnico:operario_detalle', kwargs = {
            'pk': self.object.vehiculo.operador.id
        }))

class DeleteFoto(DeleteView):
    model = Fotos_Vehiculo
    template_name = 'tecnico/foto_eliminar.html'
    def get_success_url(self, **kwargs):
        return reverse_lazy('tecnico:operario_detalle', kwargs = {
            'pk': self.kwargs['fk']})

    def get_context_data(self, *args, **kwargs):
        context = super(DeleteFoto, self).get_context_data(*args, **kwargs)
        context['llave'] = self.kwargs['fk'];
        return context

# class base views for Reports 
@method_decorator(permission_required('tecnico.verificar'), name='dispatch') 
class CreateInforme(CreateView):
    model = Informe
    template_name = 'tecnico/informe_form.html'
    form_class = InformeForm

    def get_context_data(self, *args, **kwargs):
        context = super(CreateInforme, self).get_context_data(*args, **kwargs)
        tipo = self.kwargs['tip']
        if tipo == '3':
            analisis = True
            context['analisis']=analisis
        return context

    def form_valid(self, form):
        self.object = form.save(commit = False)
        operador = Operador_Nuevo.objects.get(id=self.kwargs['pk'])
        self.object.operador = operador
        tipo = self.kwargs['tip']
        if tipo == '1':
            self.object.tipo = 'OBSERVACION'
            self.object.save()
            return HttpResponseRedirect(reverse_lazy('tecnico:operario_nuevo_listar'))
        elif tipo == '2':
            self.object.tipo = 'DEVOLUCION'
            self.object.save()
            operador.vigente = False
            operador.save()
            nota = Nota.objects.get(operador_n=operador.id)
            nota.devuelto = True
            nota.save()
            return HttpResponseRedirect(reverse_lazy('tecnico:informe_devol', kwargs = {'pk': self.kwargs['pk']}))
        elif tipo == '3':
            self.object.tipo = 'INFORME_TECNICO'
            self.object.save()
            return HttpResponseRedirect(reverse_lazy('tecnico:operario_nuevo_listar'))

class informeObs(View):
    def encabezado_pie(self, pdf, document):
        pdf.saveState()
        logo_gober = settings.MEDIA_ROOT+'/informes/logo7.png'
        logo_transporte = settings.MEDIA_ROOT+'/informes/logo_transporte.jpg'
        #Definimos el tamaño de la imagen a cargar y las coordenadas correspondientes
        pdf.drawImage(logo_gober, 100, 680, 60, 60,preserveAspectRatio=True)
        pdf.drawImage(logo_transporte, 450, 690, 80, 50)
        #Establecemos el tamaño de letra en 16 y el tipo de letra Helvetica
        pdf.setFont("Times-BoldItalic", 12)
        #Dibujamos una cadena en la ubicación X,Y especificada
        pdf.drawString(190, 720, u"Gobierno Autónomo Departamental de Potosí")
        pdf.setFont("Times-BoldItalic", 12)
        pdf.drawString(220, 700, u"Secretaría Jurídica Departamental")
        pdf.setFont("Times-Roman", 8.5)
        pdf.drawString(440, 680, u"UNIDAD DE TRANSPORTE")
        logo_dakar = settings.MEDIA_ROOT+'/informes/logo_dakar.jpg'
        logo_banderas = settings.MEDIA_ROOT+'/informes/logo_banderas_pb.png'
        #Definimos el tamaño de la imagen a cargar y las coordenadas correspondientes
        pdf.drawImage(logo_dakar, 100, 10, 60, 50)
        pdf.drawImage(logo_banderas, 180, 12, 250, 15, mask='auto')
        pdf.roundRect(450, 10, 100, 40, 5, stroke = 1)
        pdf.setFont("Times-Roman", 6)
        pdf.drawString(476, 40, u"Secretaría Jurídica")
        pdf.drawString(460, 33, u"Plaza de Armas 10 de Noviembre")
        pdf.drawString(476, 26, u"Teléfono 62 29292")
        pdf.drawString(483, 19, u"Fax 6227477")
        pdf.restoreState()

    def informe_obs(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "informe_obs",  alignment=TA_RIGHT, fontSize=10, fontName="Times-Roman"))
        informe = Informe.objects.get(operador=operador.id, tipo='OBSERVACION')
        text = 'Potosí, {}/{}/{}'.format(informe.fecha.day, informe.fecha.month, informe.fecha.year)
        para = Paragraph(text, styles["informe_obs"] )
        floables.append(para)
        text = 'Cite ADM/URRT/DJD Nº {}/{}'.format(informe.cite, informe.fecha.year)
        para = Paragraph(text, styles["informe_obs"] )
        floables.append(para)

    def dirigido(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "dirigido",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman"))
        floables.append(spacer)
        text = 'Señor:'
        para = Paragraph(text, styles["dirigido"] )
        floables.append(para)
        nota = Nota.objects.get(operador_n=operador.id)
        text = '{}.'.format(nota.representante_ente)
        para = Paragraph(text, styles["dirigido"] )
        floables.append(para)
        text = '{} DE(LA) {}.'.format(nota.cargo_repr.upper(), nota.nombre_ente.upper())
        para = Paragraph(text, styles["dirigido"] )
        floables.append(para)
    
    def referencia(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "ref",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman"))
        floables.append(spacer)
        text = 'Presente.-'
        para = Paragraph(text, styles["ref"] )
        floables.append(para)
        if (operador.razon_social.id ==1):
            text = 'Ref.: DOCUMENTOS OBSERVADOS DEL {}'.format(operador.nombre.upper())
        else:
            text = 'Ref.: DOCUMENTOS OBSERVADOS DE LA {}'.format(operador.nombre.upper())
        para = Paragraph(text, styles["ref"] )
        floables.append(para)

    def inicio_carta(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "inicio",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman"))
        nota = Nota.objects.get(operador_n=operador.id)
        floables.append(spacer)
        text = 'De mi mayor consideración:'
        para = Paragraph(text, styles["inicio"] )
        floables.append(para)
        floables.append(spacer)
        text = '''La Unidad de Registro y Regulación de Transporte dependiente de la Secretaría Jurídica del Gobierno Autónomo Departamental de Potosí, ha recibido lo siguiente: la nota del {}/{}/{} con Cite Nº {}/{} del {} afiliados a la {}, donde se solicita tramite de Tarjetas de Operación por lo que se tiene las siguientes observaciones:
        '''.format(
            nota.fecha.day,
            nota.fecha.month,
            nota.fecha.year,
            nota.cite,
            nota.fecha.year,
            operador.nombre.title(),
            nota.nombre_ente
        )
        para = Paragraph(text, styles["inicio"] )
        floables.append(para)        

    def obs_operador(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "obs_op",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman",bulletFontSize = 1,bulletOffsetY = -1.5, leftIndent = 35.8, bulletText="*"),alias='ul')
        checklist_op = Checklist_Operario.objects.filter(operador_nuevo=operador.id, cumple=False)
        for i in checklist_op:
            text = '{}.'.format(i.observacion)
            para = Paragraph(text, styles["obs_op"] )
            floables.append(para)
            floables.append(Spacer(1, 3))

    def obs_vehiculos(self, floables, spacer, styles, operador, vehi_obs_ids):
        styles.add(ParagraphStyle(name = "obs_vehi",  alignment=TA_LEFT, fontSize=10, fontName="Times-Roman"))
        styles.add(ParagraphStyle(name = "obs_vehi_title",  alignment=TA_CENTER, fontSize=10, fontName="Times-Roman"))
        floables.append(spacer)
        text = 'PARQUE AUTOMOTOR OBSERVADO'
        para = Paragraph(text, styles["obs_vehi_title"] )
        floables.append(para)
        floables.append(spacer)
        vehiculos_obs = Vehiculo_Nuevo.objects.filter(id__in=vehi_obs_ids)
        
        encabezado_tabla=['No.', 'Nombre y apellido', 'Placa', 'Observaciones']
        data = [encabezado_tabla]
        num = 1
        for vehiculo in vehiculos_obs:
            observaciones = Checklist_Vehiculo.objects.filter(vehiculo_nuevo=vehiculo.id, cumple=False)
            fila = []
            fila.append(Paragraph(str(num), styles["obs_vehi"]))
            fila.append(Paragraph(vehiculo.propietario.title(), styles["obs_vehi"]))
            fila.append(Paragraph(vehiculo.placa, styles["obs_vehi"]))
            textobs2 = ''
            ob = observaciones.count()
            for obs in range(ob):
                if (ob-1 == obs):
                    textobs2 += str(observaciones[obs].observacion.capitalize())
                else:
                    textobs2 += str(observaciones[obs].observacion.capitalize()) + ', '
            fila.append(Paragraph(textobs2, styles["obs_vehi"]))
            data.append(fila)
            num += 1

        tabla = Table(data = data, style = [('GRID',(0,0),(-1,-1),0.5,colors.grey),], colWidths=[22,150,60,210] )
        floables.append(tabla)

    def fin_carta(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "fin",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman"))
        floables.append(spacer)
        if (operador.razon_social.id == 1):
            text = '''Es en este sentido que el {}, no cumplen los requisitos exigidos por la Unidad de Transporte segun el Reglameto de Transporte Interprovincial e Intermunicipal de carga y/o pasajeros del Departamento de Potosí para trámite de tarjetas de operaciones teniendo un lapso de cinco días hábiles desde la recepción de la presente para subsanar, caso contrario se efectuará la devolución de la documentación.'''.format(operador.nombre)
        else:
            text = '''Es en este sentido que la {}, no cumplen los requisitos exigidos por la Unidad de Transporte segun el Reglameto de Transporte Interprovincial e Intermunicipal de carga y/o pasajeros del Departamento de Potosí para trámite de tarjetas de operaciones teniendo un lapso de cinco días hábiles desde la recepción de la presente para subsanar, caso contrario se efectuará la devolución de la documentación.'''.format(operador.nombre)

        para = Paragraph(text, styles["fin"] )
        floables.append(para)

    def firma(self, floables, spacer, styles):
        styles.add(ParagraphStyle(name = "firma",  alignment=TA_CENTER, fontSize=10, fontName="Times-Roman"))
        floables.append(spacer)
        floables.append(spacer)
        floables.append(spacer)
        floables.append(spacer)
        floables.append(spacer)
        text = '''Abg. Ángela Berrios Lizarazu'''
        para = Paragraph(text, styles["firma"] )
        floables.append(para)
        text = '''TECNICO II UNIDAD DE REGISTRO Y REGULACIÓN DE TRANSPORTE'''
        para = Paragraph(text, styles["firma"] )
        floables.append(para)

    def get(self, request, *args, **kwargs):
        #Indicamos el tipo de contenido a devolver, en este caso un pdf
        response = HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename="First-PDF.pdf"'
        #La clase io.BytesIO permite tratar un array de bytes como un fichero binario, se utiliza como almacenamiento temporal
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize= letter,
                                rightMargin = 63,
                                leftMargin = 100,
                                topMargin = 115,
                                bottomMagin= 48,
                                showBoundary = False)
        styles = getSampleStyleSheet()
        flowables = []
        spacer = Spacer(1, 0.25*inch)
        # Obtener al operador
        operador = Operador_Nuevo.objects.get(id=self.kwargs['pk'])
        # Que vehiculos estan observados
        vehiculos = Vehiculo_Nuevo.objects.filter(operador=operador.id)
        vehi_obs_ids = []
        for vehiculo in vehiculos:
            # if Checklist_Vehiculo.objects.filter(vehiculo_nuevo__in=vehiculo, cumple= False).exists():
            if Checklist_Vehiculo.objects.filter(vehiculo_nuevo=vehiculo.id, cumple=False).exists():
                vehi_obs_ids.append(vehiculo.id)

        self.informe_obs(flowables, spacer, styles, operador)
        self.dirigido(flowables, spacer, styles, operador)
        self.referencia(flowables, spacer, styles, operador)
        self.inicio_carta(flowables, spacer, styles, operador)
        self.obs_operador(flowables, spacer, styles, operador)
        if vehi_obs_ids != []:
            self.obs_vehiculos(flowables, spacer, styles, operador, vehi_obs_ids)
        self.fin_carta(flowables, spacer, styles, operador)
        self.firma(flowables, spacer, styles)

        doc.build(flowables, onFirstPage=self.encabezado_pie, onLaterPages=self.encabezado_pie)
        response.write(buffer.getvalue())
        buffer.close()
        return response

class informeDevol(View):
    def encabezado_pie(self, pdf, document):
        pdf.saveState()
        logo_gober = settings.MEDIA_ROOT+'/informes/logo7.png'
        logo_transporte = settings.MEDIA_ROOT+'/informes/logo_transporte.jpg'
        #Definimos el tamaño de la imagen a cargar y las coordenadas correspondientes
        pdf.drawImage(logo_gober, 100, 680, 60, 60,preserveAspectRatio=True)
        pdf.drawImage(logo_transporte, 450, 690, 80, 50)
        #Establecemos el tamaño de letra en 16 y el tipo de letra Helvetica
        pdf.setFont("Times-BoldItalic", 12)
        #Dibujamos una cadena en la ubicación X,Y especificada
        pdf.drawString(190, 720, u"Gobierno Autónomo Departamental de Potosí")
        pdf.setFont("Times-BoldItalic", 12)
        pdf.drawString(220, 700, u"Secretaría Jurídica Departamental")
        pdf.setFont("Times-Roman", 8.5)
        pdf.drawString(440, 680, u"UNIDAD DE TRANSPORTE")
        logo_dakar = settings.MEDIA_ROOT+'/informes/logo_dakar.jpg'
        logo_banderas = settings.MEDIA_ROOT+'/informes/logo_banderas_pb.png'
        #Definimos el tamaño de la imagen a cargar y las coordenadas correspondientes
        pdf.drawImage(logo_dakar, 100, 10, 60, 50)
        pdf.drawImage(logo_banderas, 180, 12, 250, 15, mask='auto')
        pdf.roundRect(450, 10, 100, 40, 5, stroke = 1)
        pdf.setFont("Times-Roman", 6)
        pdf.drawString(476, 40, u"Secretaría Jurídica")
        pdf.drawString(460, 33, u"Plaza de Armas 10 de Noviembre")
        pdf.drawString(476, 26, u"Teléfono 62 29292")
        pdf.drawString(483, 19, u"Fax 6227477")
        pdf.restoreState()

    def informe_devol(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "informe_devol",  alignment=TA_RIGHT, fontSize=10, fontName="Times-Roman"))
        informe = Informe.objects.get(operador=operador.id, tipo='DEVOLUCION')
        text = 'Potosí, {}/{}/{}'.format(informe.fecha.day, informe.fecha.month, informe.fecha.year,)
        para = Paragraph(text, styles["informe_devol"] )
        floables.append(para)
        text = 'Cite ADM/URRT/DJD Nº {}/{}'.format(informe.cite, informe.fecha.year)
        para = Paragraph(text, styles["informe_devol"] )
        floables.append(para)
    
    def dirigido(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "dirigido",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman"))
        floables.append(spacer)
        text = 'Señor:'
        para = Paragraph(text, styles["dirigido"] )
        floables.append(para)
        nota = Nota.objects.get(operador_n=operador.id)
        text = '{}.'.format(nota.representante_ente)
        para = Paragraph(text, styles["dirigido"] )
        floables.append(para)
        text = '{} DEL(LA) {}.'.format(nota.cargo_repr.upper(), nota.nombre_ente.upper())
        para = Paragraph(text, styles["dirigido"] )
        floables.append(para)

    def referencia(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "ref",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman"))
        floables.append(spacer)
        text = 'Presente.-'
        para = Paragraph(text, styles["ref"] )
        floables.append(para)
        if (operador.razon_social.id ==1):
            text = 'Ref.: DEVOLUCION DE DOCUMENTACION DEL {}'.format(operador.nombre.upper())
        else:
            text = 'Ref.: DEVOLUCION DE DOCUMENTACION DE LA {}'.format(operador.nombre.upper())
        para = Paragraph(text, styles["ref"] )
        floables.append(para)

    def inicio_carta(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "inicio",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman"))
        nota = Nota.objects.get(operador_n=operador.id)
        floables.append(spacer)
        text = 'De mi mayor consideración:'
        para = Paragraph(text, styles["inicio"] )
        floables.append(para)
        floables.append(spacer)
        text = '''La Unidad de Registro y Regulación de Transporte dependiente de la Secretaría Jurídica del Gobierno Autónomo Departamental de Potosí, ha recibido lo siguiente: la nota del {}/{}/{} con Cite Nº {}/{} del {} afiliados a la {}, donde se solicita tramite de Tarjetas de Operación para un total de {} vehículos:
        '''.format(
            nota.fecha.day,
            nota.fecha.month,
            nota.fecha.year,
            nota.cite,
            nota.fecha.year,
            operador.nombre,
            nota.nombre_ente,
            nota.cantidad_tarjetas,
        )
        para = Paragraph(text, styles["inicio"] )
        floables.append(para)
    
    def fin_carta(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "fin",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman"))
        informe_obs = Informe.objects.get(operador=operador.id, tipo='OBSERVACION')
        floables.append(spacer)
        text = '''Es en este sentido que en fecha {}/{}/{} con Cite ADM/URRT/DJD N° {}/{} se efectuó la observación al {} quienes no subsanaron estas observaciones Hasta la fecha..'''.format(
            informe_obs.fecha.day,
            informe_obs.fecha.month,
            informe_obs.fecha.year,
            informe_obs.cite,
            informe_obs.fecha.year,
            operador.nombre,
            )
        para = Paragraph(text, styles["fin"] )
        floables.append(para)
        text = '''Teniendo estos antecedentes, se efectúa la devolución de la documentación de la documentación presentada por que no cumple con los requisitos del Reglamento de Transporte Interprovincial e Intermunicipal de Carga y/o Pasajeros del Departamento de Potosí'''
        para = Paragraph(text, styles["fin"] )
        floables.append(para)
        floables.append(spacer)
        text = '''Sin otro particular motivo, me despido con las consideraciones más distinguidas'''
        para = Paragraph(text, styles["fin"] )
        floables.append(para)

    def firma(self, floables, spacer, styles):
        styles.add(ParagraphStyle(name = "firma",  alignment=TA_CENTER, fontSize=10, fontName="Times-Roman"))
        floables.append(spacer)
        floables.append(spacer)
        floables.append(spacer)
        floables.append(spacer)
        floables.append(spacer)
        text = '''Abg. Ángela Berrios Lizarazu'''
        para = Paragraph(text, styles["firma"] )
        floables.append(para)
        text = '''TECNICO II UNIDAD DE REGISTRO Y REGULACION DE TRANSPORTE'''
        para = Paragraph(text, styles["firma"] )
        floables.append(para)

    def get(self, request, *args, **kwargs):
        #Indicamos el tipo de contenido a devolver, en este caso un pdf
        response = HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename="First-PDF.pdf"'
        #La clase io.BytesIO permite tratar un array de bytes como un fichero binario, se utiliza como almacenamiento temporal
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize= letter,
                                rightMargin = 63,
                                leftMargin = 100,
                                topMargin = 115,
                                bottomMagin= 48,
                                showBoundary = False)
        styles = getSampleStyleSheet()
        flowables = []
        spacer = Spacer(1, 0.25*inch)
        # Obtener al operador
        operador = Operador_Nuevo.objects.get(id=self.kwargs['pk'])
        # Que vehiculos estan observados
        vehiculos = Vehiculo_Nuevo.objects.filter(operador=operador.id)
        vehi_obs_ids = []
        self.informe_devol(flowables, spacer, styles, operador)
        self.dirigido(flowables, spacer, styles, operador)
        self.referencia(flowables, spacer, styles, operador)
        self.inicio_carta(flowables, spacer, styles, operador)
        self.fin_carta(flowables, spacer, styles, operador)
        self.firma(flowables, spacer, styles)
        doc.build(flowables, onFirstPage=self.encabezado_pie, onLaterPages=self.encabezado_pie)
        response.write(buffer.getvalue())
        buffer.close()
        return response

from django.utils.encoding import smart_str, smart_unicode
class informeTecnico(View):
    def encabezado_pie(self, pdf, document):
        pdf.saveState()
        logo_gober = settings.MEDIA_ROOT+'/informes/logo7.png'
        logo_transporte = settings.MEDIA_ROOT+'/informes/logo_transporte.jpg'
        #Definimos el tamaño de la imagen a cargar y las coordenadas correspondientes
        pdf.drawImage(logo_gober, 100, 680, 60, 60,preserveAspectRatio=True)
        pdf.drawImage(logo_transporte, 450, 690, 80, 50)
        #Establecemos el tamaño de letra en 16 y el tipo de letra Helvetica
        pdf.setFont("Times-BoldItalic", 12)
        #Dibujamos una cadena en la ubicación X,Y especificada
        pdf.drawString(190, 720, u"Gobierno Autónomo Departamental de Potosí")
        pdf.setFont("Times-BoldItalic", 12)
        pdf.drawString(220, 700, u"Secretaría Jurídica Departamental")
        pdf.setFont("Times-Roman", 8.5)
        pdf.drawString(440, 680, u"UNIDAD DE TRANSPORTE")
        logo_dakar = settings.MEDIA_ROOT+'/informes/logo_dakar.jpg'
        logo_banderas = settings.MEDIA_ROOT+'/informes/logo_banderas_pb.png'
        #Definimos el tamaño de la imagen a cargar y las coordenadas correspondientes
        pdf.drawImage(logo_dakar, 100, 10, 60, 50)
        pdf.drawImage(logo_banderas, 180, 12, 250, 15, mask='auto')
        pdf.roundRect(450, 10, 100, 40, 5, stroke = 1)
        pdf.setFont("Times-Roman", 6)
        pdf.drawString(476, 40, u"Secretaría Jurídica")
        pdf.drawString(460, 33, u"Plaza de Armas 10 de Noviembre")
        pdf.drawString(476, 26, u"Teléfono 62 29292")
        pdf.drawString(483, 19, u"Fax 6227477")
        pdf.restoreState()

    def informe_tecnico(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "informe_tecnico",  alignment=TA_CENTER, fontSize=13, fontName="Times-Bold"))
        informe = Informe.objects.get(operador=operador.id, tipo='INFORME_TECNICO')
        text = 'INFORME TÉCNICO'
        para = Paragraph(text, styles["informe_tecnico"])
        floables.append(para)
        text = 'URRT Nº {}/{}'.format(informe.cite, informe.fecha.year)
        para = Paragraph(text, styles["informe_tecnico"])
        floables.append(para)
    
    def dirigido(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "dirigido_a",  alignment=TA_LEFT, bulletIndent=20, fontSize=10, fontName="Times-Roman"))
        styles.add(ParagraphStyle(name = "dirigido_d",  alignment=TA_LEFT, bulletIndent=20, fontSize=10, fontName="Times-Roman"))
        styles.add(ParagraphStyle(name = "dirigido_r",  alignment=TA_LEFT, bulletIndent=20, fontSize=10, fontName="Times-Roman"))
        styles.add(ParagraphStyle(name = "dirigido_f",  alignment=TA_LEFT, bulletIndent=20, fontSize=10, fontName="Times-Roman"))
        styles.add(ParagraphStyle(name = "dirigido_bold",  alignment=TA_LEFT, fontSize=10, fontName="Times-Bold"))
        floables.append(spacer)

        data = []
        fila = []
        fila.append(Paragraph('<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; A:</p>', styles["dirigido_a"]))
        fila.append(Paragraph('Dr. Wilson Condori López', styles["dirigido_a"]))
        data.append(fila)
        fila = []
        fila.append(Paragraph('', styles["dirigido_a"]))
        fila.append(Paragraph('<strong>RESPONSABLE UNIDAD DE REGISTRO Y REGULACIÓN DE TRANSPORTE</strong>', styles["dirigido_a"]))
        data.append(fila)
        fila = []
        fila.append(Paragraph('', styles["dirigido_a"]))
        fila.append(Paragraph('', styles["dirigido_a"]))
        data.append(fila)
        fila = []
        fila.append(Paragraph('<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; DE:</p>', styles["dirigido_a"]))
        fila.append(Paragraph('Abg. Ángela Berrios Lizarazu', styles["dirigido_a"]))
        data.append(fila)
        fila = []
        fila.append(Paragraph('', styles["dirigido_a"]))
        fila.append(Paragraph('<strong>TÉCNICO II UNIDAD DE REGISTRO Y REGULACIÓN DE TRANSPORTE</strong>', styles["dirigido_a"]))
        data.append(fila)
        fila = []
        fila.append(Paragraph('', styles["dirigido_a"]))
        fila.append(Paragraph('', styles["dirigido_a"]))
        data.append(fila)
        fila = []
        fila.append(Paragraph('<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; REF.:</p>', styles["dirigido_a"]))
        if operador.razon_social_id == 1:
            text = '<strong>SOLICITUD DE TARJETAS DE OPERACIÓN A FAVOR DEL {}</strong>'.format(operador.nombre.upper())
        else:
            text = '<strong>SOLICITUD DE TARJETAS DE OPERACIÓN A FAVOR DE LA {}</strong>'.format(operador.nombre.upper())
        # text.encode('utf-16')
        fila.append(Paragraph(smart_str(text), styles["dirigido_a"]))
        data.append(fila)
        fila = []
        fila.append(Paragraph('', styles["dirigido_a"]))
        fila.append(Paragraph('', styles["dirigido_a"]))
        data.append(fila)

        informe = Informe.objects.get(operador=operador.id, tipo='INFORME_TECNICO')
        # Convertir la fecha a literal
        fecha = informe.fecha

        dia = str(fecha.day)
        if dia == '1':
            dia = '01'
        elif dia == '2':
            dia = '02'
        elif dia == '3':
            dia = '03'
        elif dia == '4':
            dia = '04'
        elif dia == '5':
            dia = '05'
        elif dia == '6':
            dia = '06'
        elif dia == '7':
            dia = '07'
        elif dia == '8':
            dia = '08'
        elif dia == '9':
            dia = '09'
        mes = str(fecha.month)
        if mes == '1':
            mes = 'enero'
        elif mes == '2':
            mes = 'febrero'
        elif mes == '3':
            mes = 'marzo'
        elif mes == '4':
            mes = 'abril'
        elif mes == '5':
            mes = 'mayo'
        elif mes == '6':
            mes = 'junio'
        elif mes == '7':
            mes = 'julio'
        elif mes == '8':
            mes = 'agosto'
        elif mes == '9':
            mes = 'septiembre'
        elif mes == '10':
            mes = 'octubre'
        elif mes == '11':
            mes = 'noviembre'
        elif mes == '12':
            mes = 'diciembre'

        anio = str(fecha.year)

        fila = []
        fila.append(Paragraph('<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; FECHA:</p>', styles["dirigido_a"]))
        fila.append(Paragraph('Potosí, {} de {} de {}'.format(dia, mes, anio), styles["dirigido_a"]))
        data.append(fila)

        tabla = Table(data = data, colWidths=[70,370], rowHeights=[15,15,30,15,15,50,15,50,5] )
        floables.append(tabla)

        text = '_______________________________________________________________________________________'
        para = Paragraph(text, styles["dirigido_a"] )
        floables.append(para)

        # text = '<bullet>A:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</bullet>Dr. Wilson Condori López'
        # print(text)
        # para = Paragraph(text, styles["dirigido_a"] )
        # floables.append(para)
        # text = '<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</p>RESPONSABLE UNIDAD DE REGISTRO Y REGULACIÓN DE TRANSPORTE'
        # para = Paragraph(text, styles["dirigido_bold"] )
        # floables.append(para)
        # floables.append(spacer)
        # text = '<bullet>De:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</bullet>Lic. Lourdes Arce Quispe'
        # para = Paragraph(text, styles["dirigido_d"] )
        # floables.append(para)
        # text = '<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</p>TÉCNICO II UNIDAD DE REGISTRO Y REGULACIÓN DE TRANSPORTE'
        # para = Paragraph(text, styles["dirigido_bold"] )
        # floables.append(para)
        # floables.append(spacer)
        # floables.append(spacer)
        # if operador.razon_social_id == 1:
        #     text = '<bullet>Ref.:&nbsp;&nbsp;&nbsp;&nbsp;</bullet><strong>SOLICITUD DE TARJETAS DE OPERACIÓN A FAVOR DEL</strong>'
        # else:
        #     text = '<bullet>Ref.:&nbsp;&nbsp;&nbsp;&nbsp;</bullet><strong>SOLICITUD DE TARJETAS DE OPERACIÓN A FAVOR DE LA</strong>'
        # para = Paragraph(text, styles["dirigido_r"] )
        # floables.append(para)
        # text = '<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</p>{}'.format(operador.nombre.upper())
        # para = Paragraph(text, styles["dirigido_bold"] )
        # floables.append(para)
        # floables.append(spacer)
        # floables.append(spacer)

        # informe = Informe.objects.get(operador=operador.id, tipo='INFORME_TECNICO')
        # # Convertir la fecha a literal
        # fecha = informe.fecha
        # dia = str(fecha.day)
        # if dia == '1':
        #     dia = '01'
        # elif dia == '2':
        #     dia = '02'
        # elif dia == '3':
        #     dia = '03'
        # elif dia == '4':
        #     dia = '04'
        # elif dia == '5':
        #     dia = '05'
        # elif dia == '6':
        #     dia = '06'
        # elif dia == '7':
        #     dia = '07'
        # elif dia == '8':
        #     dia = '08'
        # elif dia == '9':
        #     dia = '09'
        # mes = str(fecha.month)
        # if mes == '1':
        #     mes = 'enero'
        # elif mes == '2':
        #     mes = 'febrero'
        # elif mes == '3':
        #     mes = 'marzo'
        # elif mes == '4':
        #     mes = 'abril'
        # elif mes == '5':
        #     mes = 'mayo'
        # elif mes == '6':
        #     mes = 'junio'
        # elif mes == '7':
        #     mes = 'julio'
        # elif mes == '8':
        #     mes = 'agosto'
        # elif mes == '9':
        #     mes = 'septiembre'
        # elif mes == '10':
        #     mes = 'octubre'
        # elif mes == '11':
        #     mes = 'noviembre'
        # elif mes == '12':
        #     mes = 'diciembre'
        # anio = str(fecha.year)
        # text = '<bullet>Fecha:</bullet>Potosí, {} de {} de {}'.format(dia, mes, anio)
        # para = Paragraph(text, styles["dirigido_a"] )
        # floables.append(para)
        # floables.append(spacer)

    def antecedentes(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "antec",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman"))
        styles.add(ParagraphStyle(name = "antec_bold",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Bold"))
        styles.add(ParagraphStyle(name = "center",  alignment=TA_CENTER, fontSize=10, fontName="Times-Bold"))
        styles.add(ParagraphStyle(name = "antc_bullet",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman"),alias='ul')
        styles.add(ParagraphStyle(name = "antc_bullet_1",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman", bulletText="-"),alias='cl')
        nota = Nota.objects.get(operador_n=operador.id)
        floables.append(spacer)
        text = 'I ANTECEDENTES.'
        para = Paragraph(text, styles["antec_bold"] )
        floables.append(para)
        if operador.es_nuevo == True:
            if operador.razon_social_id == 1:
                text = 'La {}, en representación del {} mediante Nota con Cite N° {}/{} solicita Tarjetas de Operación, presentando la documentación correspondiente y exigida por la Unidad de Transporte según el Reglamento de Transporte Interprovincial e Intermunicipal de carga y/o pasajeros del Departamento de Potosí:'.format(
                    nota.nombre_ente, 
                    operador.nombre.title(),
                    nota.cite,
                    nota.fecha.year,
                    )
            else:
                text = 'La {}, en representación de la {} mediante Nota con Cite N° {}/{} solicita Tarjetas de Operación, presentando la documentación correspondiente y exigida por la Unidad de Transporte según el Reglamento de Transporte Interprovincial e Intermunicipal de carga y/o pasajeros del Departamento de Potosí:'.format(
                    nota.nombre_ente, 
                    operador.nombre.title(),
                    nota.cite,
                    nota.fecha.year,
                   )
            para = Paragraph(text, styles["antec"] )
            floables.append(para)
        else:
            if operador.razon_social_id == 1:
                text = 'El {} en representación de(la) {} mediante Cite N° {}/{} solicita la renovación de Tarjetas de Operación para su parque automotor, presentando la documentacion correspondiente y exigida por la Unidad de Transporte según el Reglamento de Transporte Interprovincial eIntermunicipal de carga y/o pasajeros del Departamento de Potosí:'.format(
                    nota.nombre_ente,
                    operador.nombre.title(),
                    nota.cite,
                    nota.fecha.year,
                    )
            else:
                text = 'La {} en representación de(la) {} mediante Cite N° {}/{} solicita la renovación de Tarjetas de Operación para su parque automotor, presentando la documentacion correspondiente y exigida por la Unidad de Transporte según el Reglamento de Transporte Interprovincial eIntermunicipal de carga y/o pasajeros del Departamento de Potosí:'.format(
                    nota.nombre_ente,
                    operador.nombre.title(),
                    nota.cite,
                    nota.fecha.year,
                    )
            para = Paragraph(text, styles["antec"])
            floables.append(para)
        floables.append(spacer)
        if operador.es_nuevo == True:
            rs = Razon_Social.objects.get(nombre = operador.razon_social)
            # print('-c-c-c-c-c-c-c'+str(rs))
            queryset_requisitos = requisitos_razon_social.objects.filter(razon_social = rs).order_by('id')
            # print('-c-c-c-c-c-c-c'+str(queryset_requisitos))
            lista = []
            for a in queryset_requisitos:
                lista.append(a.requisitos_rs.id)
                # print ('//////////------' + str(lista))
            requisitos = Requisitos_RS.objects.filter(id__in=lista)
            # print ('//////////------' + str(requisitos))
            if requisitos:
                text = 'OBSERVACIONES AL OPERADOR'
                para = Paragraph(text, styles["center"])
                floables.append(para)
                floables.append(Spacer(1, 10))

            for requisito in requisitos:
                text = '<bullet>&#9679; &nbsp;&nbsp;</bullet>{}'.format(requisito)
                para = Paragraph(text, styles["antc_bullet"])
                floables.append(para)
                floables.append(Spacer(1, 10))
            
            floables.append(spacer)
            requisitos_vehiculos = Requisitos_Vehi.objects.exclude(id=7)
            # print ('//////////------' + str(requisitos_vehiculos))
            for requisito in requisitos_vehiculos:
                text = '{}'.format(requisito.descripcion)
                para = Paragraph(text, styles["antc_bullet_1"])
                floables.append(para)
                floables.append(Spacer(1, 10))

    def analisis_tecnico(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "analisis",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman"))
        styles.add(ParagraphStyle(name = "analisis_bold",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Bold"))
        styles.add(ParagraphStyle(name = "analisis_center_bold",  alignment=TA_CENTER, fontSize=10, fontName="Times-Bold"))
        styles.add(ParagraphStyle(name = "analisis_left_bold",  alignment=TA_LEFT, fontSize=10, fontName="Times-Bold"))
        styles.add(ParagraphStyle(name = "analisis_center",  alignment=TA_CENTER, fontSize=10, fontName="Times-Roman"))
        styles.add(ParagraphStyle(name = "analisis_bullet",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman", bulletText="*"))
        floables.append(spacer)
        text = 'II ANÁLISIS TÉCNICO.'
        para = Paragraph(text, styles["analisis_bold"] )
        floables.append(para)
        floables.append(spacer)
        text = 'Revisada la documentación presentada se determina lo siguiente:'
        para = Paragraph(text, styles["analisis"] )
        floables.append(para)
        floables.append(spacer)
        nota = Nota.objects.get(operador_n=operador.id)
        if operador.razon_social_id == 1:
            text = '1.- La solicitud presentada por el {} ha sido presentada por su Ente Matriz - {}.'.format(
                operador.nombre.title(),
                nota.nombre_ente,
           )
        else:
            text = '1.- La solicitud presentada por la {} ha sido presentada por su Ente Matriz - {}.'.format(
                operador.nombre.title(),
                nota.nombre_ente,
            )
        para = Paragraph(text, styles["analisis"] )
        floables.append(para)
        floables.append(spacer)
        if operador.es_nuevo == True:
            if operador.razon_social_id == 1:
                text = '2.- RUTA SOLICITADA POR EL {}'.format(operador.nombre.upper())
            else:
                text = '2.- RUTA SOLICITADA POR LA {}'.format(operador.nombre.upper())
            para = Paragraph(text, styles["analisis_center_bold"] )
            floables.append(para)
            floables.append(spacer)
            text = '{}'.format(nota.ruta_solicitada.upper())
            para = Paragraph(text, styles["analisis_center"] )
            floables.append(para)
            floables.append(spacer)
        else:
            if operador.razon_social_id == 1:
                text = 'El {}, tiene la siguiente ruta autorizada'.format(operador.nombre,)
            else:
                text = 'La {}, tiene la siguiente ruta autorizada'.format(operador.nombre,)
            para = Paragraph(text, styles["analisis_bullet"])
            floables.append(para)
            floables.append(spacer)
            if operador.razon_social_id == 1:
                text = 'RUTA AUTORIZADA DEL {}'.format(operador.nombre.upper())
            else:
                text = 'RUTA AUTORIZADA DE LA {}'.format(operador.nombre.upper())
            para = Paragraph(text, styles["analisis_bold"])
            floables.append(para)
            floables.append(spacer)
            floables.append(spacer)
            floables.append(spacer)
            #Poner Ruta Una vez que sea registrado el operador nuevo
            floables.append(spacer)
            if operador.razon_social_id == 1:
                text = '3.- El {} solicitó renovación de Tarjetas de Operación para el siguiente parque automotor:'.format(operador.nombre)
            else:
                text = '3.- La {} solicitó renovación de Tarjetas de Operación para el siguiente parque automotor:'.format(operador.nombre)
            para = Paragraph(text, styles["analisis_bullet"])
            floables.append(para)
            text = 'PARQUE AUTOMOTOR RENOVACION'
            para = Paragraph(text, styles["analisis_center_bold"] )
            floables.append(para)

            vehiculos = Vehiculo_Nuevo.objects.filter(operador=operador.id)
            encabezado_tabla=['No.', 'Nombre y apellido', 'Placa']
            data = [encabezado_tabla]
            num = 1
            for vehiculo in vehiculos:
                fila = []
                fila.append(Paragraph(str(num), styles["analisis"]))
                fila.append(Paragraph(vehiculo.propietario, styles["analisis"]))
                fila.append(Paragraph(vehiculo.placa, styles["analisis"]))
                data.append(fila)
                num += 1
            tabla = Table(data = data, style = [('GRID',(0,0),(-1,-1),0.5,colors.grey),], colWidths=[22,150,60,210] )
            floables.append(tabla)

        if operador.razon_social_id == 1:
            text = '3.- El {} solicita Tarjetas de Operación Interprovincial para el siguiente parque automotor:'.format(operador.nombre.title())
        else:
            text = '3.- La {} solicita Tarjetas de Operación Interprovincial para el siguiente parque automotor:'.format(operador.nombre.title())
        para = Paragraph(text, styles["analisis_bullet"] )
        floables.append(para)
        floables.append(spacer)
        text = 'PARQUE AUTOMOTOR'
        para = Paragraph(text, styles["analisis_center_bold"] )
        floables.append(para)
        floables.append(spacer)
        vehiculos = Vehiculo_Nuevo.objects.filter(operador=operador.id)
        encabezado_tabla=['No.', 'Nombre y apellido', 'Placa', 'Tipo']
        data = [encabezado_tabla]
        num = 1
        for vehiculo in vehiculos:
            fila = []
            fila.append(Paragraph(str(num), styles["analisis"]))
            fila.append(Paragraph(vehiculo.propietario, styles["analisis"]))
            fila.append(Paragraph(vehiculo.placa, styles["analisis"]))
            fila.append(Paragraph(vehiculo.tipo_vehiculo, styles["analisis"]))
            data.append(fila)
            num += 1
        # print('++++++++****'+ str(data))

        tabla = Table(data = data, style = [('GRID',(0,0),(-1,-1),0.5,colors.black),('BACKGROUND',(0,0),(3,0),colors.grey),('TEXTCOLOR',(0,0),(3,0),colors.white)], colWidths=[22,150,60,100] )
        floables.append(tabla)
        floables.append(spacer)

        #Porcion de codigo para controlar a los documentos observados el la DB
        if Informe.objects.filter(operador=operador.id, tipo='OBSERVACION', vigente=True).exists():
            inf = Informe.objects.filter(operador=operador.id, tipo='OBSERVACION', vigente=True)
            for i in inf:
                i.vigente = False
                i.save()

        informe = Informe.objects.get(operador=operador.id, tipo='INFORME_TECNICO')
        text = '4.- {}'.format(informe.ans_tecnico)
        para = Paragraph(text, styles["analisis_bullet"])
        floables.append(para)
        floables.append(spacer)
        text = 'MUESTRARIO FOTOGRÁFICO'
        para = Paragraph(text, styles["analisis_center_bold"])
        floables.append(para)
        floables.append(spacer)
        for vehiculo in vehiculos:
            text = 'PLACA: {}'.format(vehiculo.placa)
            para = Paragraph(text, styles["analisis_left_bold"])
            floables.append(para)
            floables.append(spacer)
            fotos = Fotos_Vehiculo.objects.filter(vehiculo=vehiculo.id)
            if fotos:
                data = []
                fila = []
                for foto in fotos:
                    text = '{}'.format(foto.foto)
                    img_fotos = settings.MEDIA_ROOT + '/' + str(text)
                    f = Image(img_fotos,200,200)
                    fila.append(f) 
                data.append(fila)
                tabla = Table(data = data)
                # tabla.setStyle(TableStyle([('BOX',(0,0),(-1,-1),0.5,colors.grey)]))
                floables.append(tabla)
                    
        floables.append(spacer)
        text = 'III CONCLUSIONES Y RECOMENDACIONES.'
        para = Paragraph(text, styles["analisis_bold"])
        floables.append(para)
        floables.append(spacer)
        text = '{}'.format(informe.concluciones)
        para = Paragraph(text, styles["analisis_bullet"])
        floables.append(para)

    def get(self, request, *args, **kwargs):
        #Indicamos el tipo de contenido a devolver, en este caso un pdf
        response = HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename="First-PDF.pdf"'
        #La clase io.BytesIO permite tratar un array de bytes como un fichero binario, se utiliza como almacenamiento temporal
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize= letter,
                                rightMargin = 63,
                                leftMargin = 100,
                                topMargin = 115,
                                bottomMagin= 48,
                                showBoundary = False)
        styles = getSampleStyleSheet()
        flowables = []
        spacer = Spacer(1, 0.25*inch)
        # Obtener al operador
        operador = Operador_Nuevo.objects.get(id=self.kwargs['pk'], vigente=True)
        # Que vehiculos estan observados
        vehiculos = Vehiculo_Nuevo.objects.filter(operador=operador.id)
        vehi_obs_ids = []
        self.informe_tecnico(flowables, spacer, styles, operador)
        self.dirigido(flowables, spacer, styles, operador)
        self.antecedentes(flowables, spacer, styles, operador)
        self.analisis_tecnico(flowables, spacer, styles, operador)
        # self.fin_carta(flowables, spacer, styles, operador)
        # self.firma(flowables, spacer, styles)
        doc.build(flowables, onFirstPage=self.encabezado_pie, onLaterPages=self.encabezado_pie)
        response.write(buffer.getvalue())
        buffer.close()
        return response

@method_decorator(permission_required('tecnico.administrar_doc_legal'), name='dispatch') 
class EmitirDocumentos(ListView):
    model = Operador_Nuevo
    template_name = 'tecnico/emitir_document.html'

    def get_queryset(self):
        querysets = super(EmitirDocumentos, self).get_queryset()
        informes = Informe.objects.filter(tipo='INFORME_TECNICO', vigente=True)
        #print('ñññññññññññññññññ'+ str(informes))
        operador_in_informe_tecnico = []
        for informe in informes:
            operador_in_informe_tecnico.append(informe.operador.id)
        #print('ñññññññññññññññññ'+ str(operador_in_informe_tecnico))
        queryset_operado_in_inf_tecnico = querysets.filter(vigente=True, en_tramite=True, id__in=operador_in_informe_tecnico).order_by('id')
        return queryset_operado_in_inf_tecnico

class crearDocLeg(CreateView):
    model = Docs_Legal
    template_name = 'tecnico/legal_form.html'
    form_class = DocsForm

    def get_context_data(self, *args, **kwargs):
        context = super(crearDocLeg, self).get_context_data(*args, **kwargs)
        tipo = self.kwargs['tip']
        if tipo == '1':
            doc = True
        else:
            doc = False
        context['doc']=doc
        return context

    def form_valid(self, form):
        self.object = form.save(commit = False)
        operador = Operador_Nuevo.objects.get(id=self.kwargs['pk'])
        self.object.operador = operador
        pk = self.kwargs['pk']
        tipo = self.kwargs['tip']
        if tipo == '1':
            self.object.tipo = 'INFORME_LEGAL'
            print ('Lleeeguueeee')
            self.object.save()
            return HttpResponseRedirect(reverse_lazy('tecnico:doc_legal', kwargs = {
                'pk':self.object.id,
                'tip':tipo 
            }))
            # return HttpResponseRedirect(reverse_lazy('tecnico:listar_op_documentos'))
        elif tipo == '2':
            self.object.tipo = 'RESOLUCION_ADMINISTRATIVA'
            self.object.save()
            print ('Lleeeguueeee,,,,,,..')
            return HttpResponseRedirect(reverse_lazy('tecnico:doc_legal', kwargs = {
                'pk': self.object.id,
                'tip':tipo
            }))
            # return HttpResponseRedirect(reverse_lazy('tecnico:listar_op_documentos'))

class createDocLegal(UpdateView):
    model = Docs_Legal
    template_name = 'tecnico/documento_form.html'
    form_class = DocsLegalForm
    def form_valid(self, form):
        self.object = form.save(commit = False)

        # operador = Operador_Nuevo.objects.get(id=self.kwargs['pk'])
        # self.object.operador = operador

        tipo = self.kwargs['tip']
        if tipo == '1':
            # self.object.tipo = 'INFORME_LEGAL'
            self.object.save()
            return HttpResponseRedirect(reverse_lazy('tecnico:listar_op_documentos'))
        elif tipo == '2':
            # self.object.tipo = 'RESOLUCION_ADMINISTRATIVA'
            self.object.save()
            return HttpResponseRedirect(reverse_lazy('tecnico:listar_op_documentos'))
    
    def get_initial(self):
        doc = Docs_Legal.objects.get(id=self.kwargs['pk'])
        operador = Operador_Nuevo.objects.get(id=doc.operador_id)
        nota = Nota.objects.get(operador_n=operador.id, fenecio=False)
        if operador.es_nuevo:
            vehiculos = Vehiculo_Nuevo.objects.filter(operador=operador.id)
        else:
            vehiculos = Vehiculo_Nuevo.objects.filter(Q(operador=operador.id, renovando=True) | Q(operador=operador.id, es_nuevo=True))
        informe_tecnico = Informe.objects.get(operador=operador.id, tipo='INFORME_TECNICO', vigente=True)
        
        tipo = self.kwargs['tip']
        # a = type(operador.nombre)
        # print(a)

        table = '''
        <table align="center" id="table_rs"">
            <thead>
                <tr>
                    <th style="width: 20px; text-align: center;">No.</th>
                    <th style="width: 180px; text-align: center;">NOMBRE Y APELLIDO</th>
                    <th style="width: 80px; text-align: center;">No. DE PLACA</th>
                    <th style="width: 100px; text-align: center;">TIPO DE VEHICULO</th>
                </tr>
            </thead>
            <tbody>'''
        contador = 1
        for vehiculo in vehiculos:
            table += '''<tr>
                            <td style="text-align: center;">{}</td>
                            <td style="text-align: center;">{}</td>
                            <td style="text-align: center;">{}</td>
                            <td style="text-align: center;">{}</td>
                        </tr>'''.format(contador, vehiculo.propietario, vehiculo.placa, vehiculo.tipo_vehiculo)
            contador += 1
        table += '''</tbody></table>'''
        #Variables los informes
        operador_nombre = operador.nombre.title()
        pre='de la'
        pre1='a la'
        pre2='la'
        if operador.razon_social_id == 1:
            pre='del'
            pre1='al'
            pre2='el'
        nota_representante_ente = nota.representante_ente
        nota_cargo_repr = nota.cargo_repr
        nota_nombre_ente = nota.nombre_ente
        nota_cite = nota.cite
        nota_ruta = nota.ruta_solicitada
        nota_fecha = str(nota.fecha)
        # print('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFfffff')
        # print(type(nota_fecha))

        nota_fecha_day = str(nota.fecha.day)
        nota_fecha_month = str(nota.fecha.month)
        nota_fecha_year = str(nota.fecha.year)
        informe_tecnico_cite = informe_tecnico.cite
        informe_tecnico_fecha_year = str(informe_tecnico.fecha.year)

        if tipo == '1':
            inf_legal = Docs_Legal.objects.get(operador=operador.id, vigente=True, tipo='INFORME_LEGAL')
            anio = str(inf_legal.fecha.year)
            mes = str(inf_legal.fecha.month)
            dia = str(inf_legal.fecha.day)
            if mes == '1':
                mes='enero'
            elif mes == '2':
                mes ='febrero'
            elif mes == '3':
                mes ='marzo'
            elif mes == '4':
                mes ='abril'
            elif mes == '5':
                mes ='mayo'
            elif mes == '6':
                mes ='junio'
            elif mes == '7':
                mes ='julio'
            elif mes == '8':
                mes ='agosto'
            elif mes == '9':
                mes ='septiembre'
            elif mes == '10':
                mes ='octubre'
            elif mes == '11':
                mes ='noviembre'
            elif mes == '12':
                mes ='diciembre'

            html = '''
            <p style="margin-left:0cm; margin-right:0cm; text-align:center">
                <span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><strong><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                    INFORME LEGAL URRT/DJD N&deg; '''+ inf_legal.cite +'''/'''+ anio +'''
                </span></span></strong></span></span>
            </p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify">&nbsp;</p>
            <table>
            <thead>
            </thead>
            <tbody>
                <tr>
                    <td style="vertical-align: top; height:20px; width: 100px;">
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">A:</span></span></span></p>
                    </td>
                    <td style="vertical-align: top; height:20px; width: 849px;">
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">Abg. Juan Carlos Cejas Ugarte</span></span></span></span></p>
                        <p style="margin-left:0cm; margin-right:0cm">
                            <span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><strong><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                                GOBERNADOR DEL DEPARTAMENTO AUT&Oacute;NOMO DE POTOS&Iacute;.
                            </span></span></strong></span></span>
                        </p>
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify">&nbsp;</p>
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify">&nbsp;</p>
                    </td>
                </tr>
                <tr>
                    <td style="vertical-align: top; height:20px; width: 100px;">
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">VIA:</span></span></span></p>
                    </td>
                    <td style="vertical-align: top; height:20px; width: 849px;">
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">Abg. Daniel Antonio Apaza Barrera</span></span></span></span></p>
                        <p style="margin-left:0cm; margin-right:0cm">
                            <span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><strong><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                                DIRECTOR JUR&Iacute;DICO DEPARTAMENTAL.
                            </span></span></strong></span></span>
                        </p>
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify">&nbsp;</p>
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify">&nbsp;</p>
                    </td>
                </tr>
                <tr>
                    <td style="vertical-align: top; height:20px; width: 100px;">
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">DE:</span></span></span></p>
                    </td>
                    <td style="vertical-align: top; height:20px; width: 849px;">
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">Abg. Wilson Condori L&oacutepez;</span></span></span></span></p>
                        <p style="margin-left:0cm; margin-right:0cm">
                            <span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><strong><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                                DIRECTOR JUR&Iacute;DICO DEPARTAMENTAL.
                            </span></span></strong></span></span>
                        </p>
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify">&nbsp;</p>
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify">&nbsp;</p>
                    </td>
                </tr>
                <tr>
                    <td style="vertical-align: top; height:20px; width: 100px;">
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">REF:</span></span></span></p>
                    </td>
                    <td style="vertical-align: top;">
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">Informe Legal de la solicitud de Tarjetas de Operaciones a favor '''+pre +''' ''' + operador_nombre +'''.</span></span></span></span></p>
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify">&nbsp;</p>
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify">&nbsp;</p>
                    </td>
                </tr>
                <tr>
                    <td style="vertical-align: top; height:20px; width: 100px;">
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">FECHA:</span></span></span></p>
                    </td>
                    <td style="vertical-align: top;">
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">Potos&iacute;, '''+ dia +''' de '''+ mes +''' de '''+ anio +'''.</span></span></span></span></p>
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify">&nbsp;</p>
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify">&nbsp;</p>
                    </td>
                </tr>
            </tbody>            
            </table>

            <div style="margin-bottom:8pt; margin-left:0cm; margin-right:0cm; margin-top:0cm; text-align:center">
            <hr /></div>
            <p style="margin-left:0cm; margin-right:0cm"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><strong><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                I.- SOLICITUD.
                </span></span></strong></span></span>
            </p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                En merito a hojas de ruta 2031 de la Secretar&iacute;a Jur&iacute;dica y solicitud de Tarjetas de Operaciones realizadas mediante notas cite '''+ nota_cite +'''/'''+ nota_fecha_year +''' presentada en fecha '''+ nota_fecha_day +'''/'''+ nota_fecha_month +'''/'''+ nota_fecha_year +''' por la '''+ nota_nombre_ente +''' y habiendo cumplido con los requisitos exigidos por el Reglamento de Transporte Interprovincial e Intermunicipal de carga y/o pasajeros del Departamento de Potos&iacute;, se pone a conocimiento el presente informe para su an&aacute;lisis y consideraci&oacute;n.
                </span></span></span></span>
            </p>
            <p style="margin-left:0cm; margin-right:0cm"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><strong><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                II.- ANTECEDENTES.
                </span></span></strong></span></span>
            </p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                El Sr. '''+ nota_representante_ente +''', '''+ nota_cargo_repr +''' de la '''+ nota_nombre_ente +''' solicit&oacute; en representaci&oacute;n '''+pre +''' ''' + operador_nombre +''' Tarjetas de Operaci&oacute;n para prestar el servicio de Transporte de pasajeros a nivel Interprovincial e Interprovincial en fecha '''+ nota_fecha_day +'''/'''+ nota_fecha_month +'''/'''+ nota_fecha_year +'''.
                </span></span></span></span>
            </p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                Consiguientemente revisada la documentaci&oacute;n y realizada la inspecci&oacute;n del parque automotor en fecha 14 de agosto de 2018 se establece que 6 de 8 afiliados '''+pre +''' ''' + operador_nombre +''' cumple con los requisitos exigidos por el Reglamento de Transporte Interprovincial e Intermunicipal de carga y/o pasajeros del Departamento de Potos&iacute; para prestar el servicio de Transporte de pasajeros en nuestro Departamento, los mismos se detallan a continuaci&oacute;n:
                </span></span></span></span>
            </p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:center"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                N&Oacute;MINA DE PARQUE AUTOMOTOR
                </span></span></span></span>
            </p>
            ''' + table + '''
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                Asimismo en fecha 14 de agosto de 2018 en cumplimiento el Reglamento de Transporte Interprovincial e Interdepartamental para el departamento de Potos&iacute;, se realiz&oacute; la inspecci&oacute;n del parque automotor '''+pre +''' ''' + operador_nombre +''' en el Municipio de Llallagua verificando que los buses porten el logo distintivo que debe poseer casa veh&iacute;culo de transporte de pasajeros de la Asociaci&oacute;n al cual pertenece, mismo que se encuentra plasmado en el informe t&eacute;cnico de URRT N&deg; '''+ informe_tecnico_cite +'''/'''+ informe_tecnico_fecha_year +''' elaborado por la Abg. &Aacute;ngela Berrios Lizarazu, T&eacute;cnico de la Unidad de Registro y Regulaci&oacute;n de Transporte.
                </span></span></span></span>
            </p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                Consiguientemente le Unidad de Registro y Regulaci&oacute;n de Transporte otorg&oacute; mediante cite N&deg; URRT 124/17 de fecha 29 de septiembre de 2018 la respectiva autorizaci&oacute;n de ruta horario, a favor '''+pre +''' ''' + operador_nombre +''' bajo el siguiente detalle:
                </span></span></span></span>
            </p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:center"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                '''+nota_ruta+'''
                </span></span></span></span>
            </p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><strong><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                III.- MARCO LEGAL.
                </span></span></strong></span></span>
            </p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                De la revisi&oacute;n de la documentaci&oacute;n correspondiente '''+pre +''' ''' + operador_nombre.title() +''' presenta lo siguiente:
                </span></span></span></span>
            </p>
            <ol>
            	<li style="text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">Resoluci&oacute;n Prefectural N&deg; 278/2004 de fecha 14 de diciembre de 2014 que reconoce la Personer&iacute;a Jur&iacute;dica '''+pre +''' ''' + operador_nombre.title() +''' en fotocopia legalizada por la Unidad de Ventanilla &Uacute;nica del Gobierno Aut&oacute;nomo Departamental.</span></span></span></span></li>
            	<li style="text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">N&oacute;mina de afiliados '''+pre +''' ''' + operador_nombre.title() +'''.</span></span></span></span></li>
            	<li style="text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">N&oacute;mina del Directorio '''+pre +''' ''' + operador_nombre.title() +'''.</span></span></span></span></li>
            </ol
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                Consiguientemente de la revisi&oacute;n de la documentaci&oacute;n presentada se colige que el impetrante ha dado cumplimiento a los requisitos previstos por el Art. 4&deg; N&uacute;m. del Reglamento de transporte P&uacute;blico Terrestre Interprovincial e Intermunicipal de pasajeros y/o carga para el Departamento de Potos&iacute; lo que hace viable la solicitud de tarjetas de Operaciones.
                </span></span></span></span>
            </p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                Por otro lado se debe poner de manifiesto lo expresado por el Art. 300 Par&aacute;grafo I N&uacute;m. 9) de la Constituci&oacute;n Pol&iacute;tica del Estado que establece que son competencias exclusivas de los Gobiernos Departamentales Aut&oacute;nomos en su jurisdicci&oacute;n: &quot;transporte interprovincial, terrestre fluvial, ferrocarriles, y otros medios de transporte en el departamento&quot;.
                </span></span></span></span>
            </p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                Con ese mismo tenor la Ley General de Transporte en su Art. 21 Inc. c) describe las competencias de las Gobiernos Departamentales con referencia al Transporte Interprovincial, al expresar lo siguiente &quot;Ejercer competencias de control y fiscalizaci&oacute;n para los servicios de transporte de alcance interprovincial e intermunicipal&quot;.
                </span></span></span></span>
            </p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                Por su parte el Art. 17 de la Ley General de Transporte bajo el ep&iacute;grafe (LAS AUTORIDADES COMPETENTES), Inc. b) expresa:
                </span></span></span></span>
            </p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                b)&nbsp; &nbsp; &nbsp;Autoridad competente del nivel departamental, representante del &Oacute;rgano Ejecutivo del nivel departamental destinado a emitir pol&iacute;ticas, planificar, regular fiscalizar&nbsp;y/o administrar la ejecuci&oacute;n, gesti&oacute;n, operaci&oacute;n y control del Sistema de Transporte Integral - STI, adem&aacute;s de aprobar planes y proyectos relativos al transporte y realizar otras actividades inherentes al sector en el marco de sus atribuciones y funciones espec&iacute;ficas.
                </span></span></span></span>
            </p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                Por otro lado el Art. 31 del mismo cuerpo legal (ATRIBUCIONES DE LA AUTORIDAD REGULATORIA). Par&aacute;grafo III expresa: &quot;Las autoridades regulatorias en los diferentes niveles tendr&aacute;n las siguientes atribuciones&quot;
                </span></span></span></span>
            </p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:center"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                1. Otorgar permisos y atribuciones.
                </span></span></span></span>
            </p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                Por &uacute;ltimo el Decreto Departamental N&deg; 39/2014 de fecha 11 de marzo de 2014, modificado por el Decreto Departamental N&deg; 0226/2015 de fecha 04 de noviembre de 2015 en su Art. 1&deg; aprueba&nbsp; el Reglamento de Transporte Intermunicipal e Interprovincial de carga y/o pasajeros del Departamento de Potos&iacute;, asimismo dispone que la Unidad de Registro y Regulaci&oacute;n de Transporte del Gobierno Aut&oacute;nomo Departamental de Potos&iacute;, proceda a otorgar las&nbsp;TARJETAS DE OPERACIONES a todos los operadores del servicio de Transporte Interprovincial e Intermunicipal de carga y/o pasajeros conforme a los requisitos y condiciones exigidos en el Reglamento de Transporte.
                </span></span></span></span>
            </p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><strong><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                IV.- ANALISIS.
                </span></span></strong></span></span>
            </p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                Que en el marco de los antecedentes y conforme a las&nbsp;notas cites N&deg; '''+ nota_cite +'''/'''+ nota_fecha_year +''' presentado en fecha '''+ nota_fecha_day +'''/'''+ nota_fecha_month +'''/'''+ nota_fecha_year +''' por la '''+ nota_nombre_ente +''' en representaci&oacute;n '''+pre +''' ''' + operador_nombre +''' y en funci&oacute;n al cumplimiento de los requisitos exigidos por el Reglamento de Transporte Interprovincial e Intermunicipal de carga y/o pasajeros del Departamento de Potos&iacute; justifican la emisi&oacute;n de Tarjetas de Operaciones a favor '''+pre +''' ''' + operador_nombre +''' en funci&oacute;n a todos los antecedentes que forman parte de la solicitud.
                </span></span></span></span>
            </p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><strong><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                V.- CONCLUSIONES Y RECOMENDACIONES.
                </span></span></strong></span></span>
            </p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                De la revisi&oacute;n correspondiente a los antecedentes '''+pre +''' ''' + operador_nombre +''' se colige que cumpli&oacute;&nbsp;con todos los requisitos exigidos por el Reglamento de Transporte Interprovincial e Intermunicipal de carga y/o pasajeros del Departamento de Potos&iacute;. Consiguientemente&nbsp; conforme a procedimiento se recomienda q su Autoridad aprobar la Resoluci&oacute;n Administrativa que autoriza emisi&oacute;n de Tarjetas de Operaciones a favor '''+pre +''' ''' + operador_nombre +'''.
                </span></span></span></span>
            </p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">
                Es cuanto informo a su autoridad para fines consiguientes.
                </span></span>
            </p>'''
        elif tipo == '2':
            res_admin = Docs_Legal.objects.get(operador=operador.id, vigente=True, tipo='RESOLUCION_ADMINISTRATIVA')
            anio_n = str(res_admin.fecha.year)
            anio = str(res_admin.fecha.year)
            mes = str(res_admin.fecha.month)
            dia = str(res_admin.fecha.day)
            # Sacando el mes en literal
            if mes == '1':
                mes='enero'
            elif mes == '2':
                mes ='febrero'
            elif mes == '3':
                mes ='marzo'
            elif mes == '4':
                mes ='abril'
            elif mes == '5':
                mes ='mayo'
            elif mes == '6':
                mes ='junio'
            elif mes == '7':
                mes ='julio'
            elif mes == '8':
                mes ='agosto'
            elif mes == '9':
                mes ='septiembre'
            elif mes == '10':
                mes ='octubre'
            elif mes == '11':
                mes ='noviembre'
            elif mes == '12':
                mes ='diciembre'

            #Sacando el dia en literal
            if dia == '1':
                dia = 'un'
            elif dia == '2':
                dia ='dos'
            elif dia == '3':
                dia = 'tres'
            elif dia == '4':
                dia ='cuatro'
            elif dia == '5':
                dia = 'cinco'
            elif dia == '6':
                dia ='seis'
            elif dia == '7':
                dia = 'siete'
            elif dia == '8':
                dia ='ocho'
            elif dia == '9':
                dia = 'nueve'
            elif dia == '10':
                dia ='diez'
            elif dia == '11':
                dia = 'once'
            elif dia == '12':
                dia ='doce'
            elif dia == '13':
                dia = 'trece'
            elif dia == '14':
                dia ='catorce'
            elif dia == '15':
                dia = 'quince'
            elif dia == '16':
                dia ='dieciseis'
            elif dia == '17':
                dia = 'diecisiete'
            elif dia == '18':
                dia = 'dieciocho'
            elif dia == '19':
                dia ='diecinueve'
            elif dia == '20':
                dia = 'veinte'
            elif dia == '21':
                dia = 'veintiun'
            elif dia == '22':
                dia ='veintidos'
            elif dia == '23':
                dia = 'veintitres'
            elif dia == '24':
                dia ='veinticuatro'
            elif dia == '25':
                dia = 'veinticinco'
            elif dia == '26':
                dia ='veintiseis'
            elif dia == '27':
                dia = 'veintisiete'
            elif dia == '28':
                dia = 'veintiocho'
            elif dia == '29':
                dia ='veintinueve'
            elif dia == '30':
                dia = 'treinta'
            elif dia == '31':
                dia = 'treinta y un'

            #Sacando el anio en literal
            if anio == '2019':
                anio = 'dos mil diecinueve'
            elif anio == '2020':
                anio ='dos mil veinte'
            elif anio == '2021':
                anio = 'dos mil veintiun'
            elif anio == '2022':
                anio ='dos mil veintidos'
            elif anio == '2023':
                anio = 'dos mil veintitres'
            elif anio == '2024':
                anio ='dos mil veinticuatro'
            elif anio == '2025':
                anio = 'dos mil veinticinco'
            elif anio == '2026':
                anio ='dos mil veintiseis'
            elif anio == '2027':
                anio = 'dos mil veintisiete'
            elif anio == '2028':
                anio ='dos mil veintiocho'
            elif anio == '2029':
                anio = 'dos mil veintinueve'
            elif anio == '2030':
                anio ='dos mil treinta'
            
            html = '''
            <p style="margin-left:0cm; margin-right:0cm; text-align:center"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><strong><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">RESOLUCI&Oacute;N ADMINISTRATIVA N&deg; '''+ str(res_admin.numero_ra) +'''/'''+ anio_n +''' </span></span></strong></span></span></p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify">&nbsp;</p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><strong><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">CONSIDERANDO: </span></span></strong><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;"><span style="color: white;">espa</span>Que la Constituci&oacute;n Pol&iacute;tica de Estado en su Art. 279 deternina: El &oacute;rgano ejecutivo departamental est&aacute; dirigido por la Gobernadora o el Gobernador, en condici&oacute;n de maxima autoridad ejecutiva. </span></span></span></span></p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;"><span style="color: white;">+++++++++++++++++++</span>Que, por su parte el Art. 300 N&uacute;m. 9) de la constituci&oacute;n Pol&iacute;tica del Estado, dispone las competencias exclusivas de los Gobiernos Aut&oacute;nomos Departamentales: Transporte interprovincial terrestre, fluvial, ferrocarriles y otros medios de transporte en el departamento.</span></span></span></span></p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;"><span style="color: white;">+++++++++++++++++++</span>Que el Art. 21 de la Ley N&deg; 165 Ley General de Transporte, dispone que los Gobiernos Aut&oacute;nomos Departementales tienen las siguientes conpetencias exclusivas: a) aprobar pol&iacute;ticas departamentales de transporte e infraestructura interprovincial e intermunicipal; y c) Ejercer competencias de control y fiscalizaci&oacute;n para los servicios de transporte de alcance interprovincial e intermunicipal, asimismo&nbsp;el Art. 31 Par&aacute;grafo III N&uacute;m. 1) del mismo cuerpo legal establece las facultades de las autoridades regulatorias dentro el marco de las compencias al establecer lo siguiente: III) las autoridades regulatorias en los diferentes niveles tendr&aacute;n las siguientes atribuciones: 1) Otorgar permisos y autorizaciones.</span></span></span></span></p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;"><span style="color: white;">+++++++++++++++++++</span>Que, el Decreto Departemental N&deg; 39/2014, de fecha once de marzo de 2014, modificado por el Decreto Departamental N&deg; 0226/2015 de fecha cuatro de noviembre de 2015 en su Art. 1&deg;, aprueba el Reglamento de Transporte Interprovincial e Intermunicipal de carga y/o pasajeros del Departamento de Potos&iacute;, asimismo dispone que la Unidad de Registro y Regulaci&oacute;n de Transporte del Gobierno Aut&oacute;nomo Departemental&nbsp;de Potos&iacute;, proceda a emitir TARJETAS DE OPERACIONES a todos los operadores de servicios del Transporte Interprovincial de carga y/o pasajeros conforme a los requisitos y condiciones exigidos en el Reglamento de Transporte.</span></span></span></span></p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;"><span style="color: white;">+++++++++++++++++++</span>Que, vistos los antecedentes '''+pre +''' ''' + operador_nombre +''', Informe T&eacute;cnico&nbsp; <strong>URRT N&ordm; '''+ informe_tecnico_cite +'''/'''+ informe_tecnico_fecha_year +'''</strong>, Informe Legal <strong>URRT/DJD N&ordm; 16/2018</strong> y nota cite <strong>URRT/DJD N&ordm; 16/2018.</strong></span></span></span></span></p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;"><span style="color: white;">+++++++++++++++++++</span>Que, '''+pre2 +''' ''' + operador_nombre +''' ha cumplido con todos los requisitos exigidos por el Reglamento de Transporte Interprovincial e Intermunicipal de carga y/o pasajeros del Departamento de Potos&iacute;, para la otorgaci&oacute;n de Tarjetas de Operaciones que autoriza la Prestaci&oacute;n del servicio de Transporte Interprovincial e Intermunicipal de pasajeros.</span></span></span></span></p>
            <table>
            <thead>
            </thead>
            <tbody>
                <tr>
                    <td style="vertical-align: top; height:20px; width: 242px;">
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;"><strong>POR TANTO:</strong></span></span></span></p>
                    </td>
                    <td style="vertical-align: top; height:20px; width: 849px;">
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">El Gobernador del Departamento Aut&oacute;nomo de Potos&iacute;, como M&aacute;xima Autoridad Ejecutiva, en el marco de sus facultades previstas por Ley.</span></span></span></span></p>
                    </td>
                </tr>
                <tr>
                    <td style="vertical-align: top;">
                        <p style="margin-left:0cm; margin-right:0cm"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><strong><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">RESUELVE</span></span></strong></span></span></p>
                        <p>&nbsp;</p>
                    </td>
                    <td>
                    </td>
                </tr>
                <tr>
                    <td style="vertical-align: top;">
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;"><strong>Art. Primero:</strong></span></span></span></p>
                    </td>
                    <td style="vertical-align: top;">
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">Autorizar la emisi&oacute;n de TARJETAS DE OPERACIONES&nbsp;y Registro N&deg; 084 '''+pre +''' ''' + operador_nombre +''', mismo que lo acredita como operador de Transporte Interprovincial e Intermunicipal en el Departamento de Potos&iacute;.</span></span></span></span></p>
                        <p>&nbsp;</p>
                    </td>
                </tr>
                <tr>
                    <td style="vertical-align: top;">
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;"><strong>Art. Segundo:</strong></span></span></span></p>
                    </td>
                    <td style="vertical-align: top;">
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">La ruta autorizada '''+pre +''' ''' + operador_nombre +''' para prestar el servicio de transporte&nbsp;de pasajeros a nivel Interprovincial e Intermunicipal en el Departamento de Potos&iacute; es el siguiente:</span></span></span></span></p>
                        <p>&nbsp;</p>
                        <p style="margin-left:0cm; margin-right:0cm; text-align:center"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">POTOS&Iacute; - LLALLAGUA&nbsp; &nbsp; &nbsp; 19:00 Hrs.</span></span></span></span></p>
                        <p style="margin-left:0cm; margin-right:0cm; text-align:center"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">LLALLAGUA - POTOS&Iacute;&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; 21:30 Hrs.</span></span></span></span></p>
                        <p>&nbsp;</p>
                    </td>
                </tr>
                <tr>
                    <td style="vertical-align: top;">
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;"><strong>Art. Tercero:</strong></span></span></span></p>
                    </td>
                    <td style="vertical-align: top;">
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">Los veh&iacute;culos autorizados '''+pre +''' ''' + operador_nombre +''', para presentar el servicio de transporte de pasajeros a nivel Interprovincial e Intermunicipal en el Departamento de Potos&iacute; son los siguientes:</span></span></span></span></p>
                        
                        <p style="margin-left:0cm; margin-right:0cm; text-align:center"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">N&Oacute;MINA DE PARQUE AUTOMOTOR </span></span></span></span></p>
                        '''+ table +'''
                        <p>&nbsp;</p>
                    </td>
                </tr>
                <tr>
                    <td style="vertical-align: top;">
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;"><strong>Art. Cuarto:</strong></span></span></span></p>
                    </td>
                    <td style="vertical-align: top;">
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">Franqu&eacute;ese al interesado un ejemplar de la presente Resoluci&oacute;n, en constancia del Registro realizado por '''+pre2+''' ''' + operador_nombre +''' ante la Unidad de Registro y Regulaci&oacute;n de Transporte del Gobierno Aut&oacute;nomo Departamental de Potos&iacute;.</span></span></span></span></p>
                        <p>&nbsp;</p>
                    </td>
                </tr>
                <tr>
                    <td style="vertical-align: top;">
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;"><strong>Art. Quinto:</strong></span></span></span></p>
                    </td>
                    <td style="vertical-align: top;">
                        <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">La Unidad de Registro y Regulaci&oacute;n de Transporte queda encargada del cumplimiento de la presente Resoluci&oacute;n.</span></span></span></span></p>
                        <p>&nbsp;</p>
                    </td>
                </tr>
            </tbody>            
            </table>
            
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">Es dada en el Palacio del Gobierno Aut&oacute;nomo Departamental de Potos&iacute;, a los '''+ dia +''' d&iacute;as del mes de '''+ mes +''' de '''+ anio +''' a&ntilde;os.</span></span></span></span></p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:justify"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">Reg&iacute;strese, comuniquese y arch&iacute;vese.</span></span></span></span></p>
            <p>&nbsp;</p>
            <p>&nbsp;</p>
            <p>&nbsp;</p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:center"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><strong><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">Dr. JUAN CARLOS CEJAS UGARTE</span></span></strong></span></span></p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:center"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><strong><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">GOBERNADOR DEL DEPARTAMENTO AUT&Oacute;NOMO DE POTOS&Iacute;</span></span></strong></span></span></p>
            <p style="text-align:center">&nbsp;</p>
            <p style="text-align:center">&nbsp;</p>
            <p style="text-align:center">&nbsp;</p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:center"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><strong><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">Dr. JOS&Eacute; LUIS BARRIOS LLANOS</span></span></strong></span></span></p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:center"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><strong><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">SECRETARIO DEPARTAMENTAL DE COORDINACI&Oacute;N GENERAL</span></span></strong></span></span></p>
            <p style="text-align:center">&nbsp;</p>
            <p style="text-align:center">&nbsp;</p>
            <p style="text-align:center">&nbsp;</p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:center"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><strong><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">Dr. DANIEL ANTONIO APAZA BARRERA</span></span></strong></span></span></p>
            <p style="margin-left:0cm; margin-right:0cm; text-align:center"><span style="font-size:11pt"><span style="font-family:Calibri,sans-serif"><strong><span style="font-size:12.0pt"><span style="font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">DIRECTOR JURIDICO DEPARTAMENTAL</span></span></strong></span></span></p>
            '''
        return {
            'descripcion': html
        }

def generar_inf_legal(request,pk):
    operador = Operador_Nuevo.objects.get(id = pk)
    datos = Docs_Legal.objects.get(operador=pk, tipo='INFORME_LEGAL', vigente=True)
    response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = 'attachment; filename=Informe-Legal.pdf'
    html = """
        <!DOCTYPE html>
        <html>
            <head>
            <style>
                #table_rs{
                    border: 0.5px solid black;
                }
                table {
                    border-collapse: collapse;
                }
                td{
                    padding-top: 3px;
                }
                th{
                    background: #838687;
                    color: white;
                    padding-top:2px;
                }

            @page {
                    size: letter portrait; /* landscape, portrait */
                    background-image: url('"""+settings.IMAGENES_ROOT+"""/plantillas/plantilla_informe_legal.pdf');
                    @frame lastPage {           /* Static Frame */
                        -pdf-frame-content: header_content_izq;
                        left: 2cm; width: 512pt; top: 1.5cm; height: 3cm;
                    }
                    @frame header_frame {           /* Static Frame */
                        -pdf-frame-content: header_content_cen;
                        left: 0cm; width: 100%; top: 1.5cm; height: 3cm;
                    }
                    @frame header_frame {           /* Static Frame */
                        -pdf-frame-content: header_content_der;
                        left: 17cm; width: 512pt; top: 1.5cm; height: 3cm;
                        
                    }
                    @frame content_frame {          /* Content Frame */
                        left: 2cm; width: 18cm; top: 5cm; height: 20cm;
                    }
                    @frame footer_frame {           /* Another static Frame */
                        -pdf-frame-content: footer_content;
                        left: 0cm; width: 100%; top: 26cm; height: 3cm;
                    }
                }
                
            </style>
            </head>

            <body >
                <!-- HTML Content -->
                <div class='content_frame'>"""+ str(datos.descripcion) +"""</div> 
            </body>
        </html>
        """
    # create a pdf
    pisaStatus = pisa.CreatePDF(html, dest=response)
    # if error then show some funy view
    if pisaStatus.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def generar_res_administrativa(request,pk):
    operador = Operador_Nuevo.objects.get(id = pk)
    datos = Docs_Legal.objects.get(operador=pk, tipo='RESOLUCION_ADMINISTRATIVA', vigente=True)
    response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = 'attachment; filename=Informe-Legal.pdf'
    numero = str(datos.numero_ra)
    anio = str(datos.fecha.year)
    html = """
    <!DOCTYPE html>
    <html>
        <head>
        <style>
            #table_rs{
                border: 0.5px solid black;
            }
            table {
                border-collapse: collapse;
            }
            td{
                padding-top: 3px;
            }
            th{
                background: #838687;
                color: white;
                padding-top:2px;
            }
        @page {
                size: legal portrait; /* landscape, portrait */
                background-image: url('"""+settings.IMAGENES_ROOT+"""/plantillas/plantilla_resolucion_administrativa.pdf');
                @frame lastPage {           /* Static Frame */
                    -pdf-frame-content: header_content_izq;
                    left: 2cm; width: 512pt; top: 1.5cm; height: 3cm;
                }
                @frame header_frame {           /* Static Frame */
                    -pdf-frame-content: header_content_cen;
                    left: 0cm; width: 100%; top: 1.5cm; height: 3cm;
                }
                @frame header_frame {           /* Static Frame */
                    -pdf-frame-content: header_content_der;
                    left: 17cm; width: 512pt; top: 1.5cm; height: 3cm;
                    
                }
                @frame content_frame {          /* Content Frame */
                    left: 3cm; width: 16cm; top: 4cm; height: 28cm;
                }
                @frame footer_frame {           /* Another static Frame */
                    -pdf-frame-content: footer_content;
                    left: 3.5cm; width: 15cm; top: 34.3cm; height: 3cm;
                }
            }
            
        </style>
        </head>
        <body >
            <!-- HTML Content -->
            <div class='content_frame'>"""+ str(datos.descripcion) +"""</div> 
            <div id="footer_content">
                <div style="display:inline-block"><pdf:pagenumber></div> <p style="display:inline-block">&nbsp; &nbsp; &nbsp; &nbsp;RESOLUCIÓN ADMINISTRATIVA N° """+ numero +"""/"""+ anio +"""</p>
                <p style="margin-top: -55px;">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;S.J.D./W.C.L.</p>
            </div>
        </body>
    </html>
    """
    # create a pdf
    pisaStatus = pisa.CreatePDF(html, dest=response)
    # if error then show some funy view
    if pisaStatus.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

# Renovacion de tarjetas
@method_decorator(permission_required('tecnico.verificar'), name='dispatch') 
class ListarOperadorR(ListView):
    model = Operador_Nuevo
    template_name = 'tecnico/operador_renovacion_listar.html'
    
    def get_context_data(self, *args, **kwargs):
        context = super(ListarOperadorR, self).get_context_data(*args, **kwargs)
        # Q(vigente= True,es_nuevo= True,en_tramite= True) | Q(es_nuevo= False, en_tramite=True)
        operador_n = Operador_Nuevo.objects.filter(
            Q(vigente=True, es_nuevo= False, en_tramite= True, renovando=True))
        context['operador_n'] = operador_n
        
        # Algoritmo para determinar si el operador esta listo para ser verificado.
        list_id = []
        for op in operador_n:
            # if Vehiculo_Nuevo.objects.filter(Q(operador=op.id, renovando=True) | Q(operador=op.id, renovando=False)).exists() and Nota.objects.filter(operador_n=op.id, fenecio=False).exists():
            if Nota.objects.filter(operador_n=op.id, fenecio=False).exists():
                nota = Nota.objects.get(operador_n=op.id, fenecio=False)
                if Vehiculo_Nuevo.objects.filter(Q(operador=op.id, renovando=True) | Q(operador=op.id, renovando=False)).count() == nota.cantidad_tarjetas:
                    list_id.append(op.id)
        operador_v = Operador_Nuevo.objects.filter(id__in=list_id)
        context['operador_v'] = operador_v
        
        # Algoritmo para determinar si el operador ha sido verificado
        list_verifi = []
        for op in operador_v:
            vehiculos = Vehiculo_Nuevo.objects.filter(operador=op.id)
            for vehiculo in vehiculos:
                if Checklist_Vehiculo.objects.filter(vehiculo_nuevo=vehiculo.id, vigente=True).exists():
                    list_verifi.append(op.id)
        operador_inf = Operador_Nuevo.objects.filter(id__in=list_verifi)
        context['operador_inf'] = operador_inf

        return context

# Intento, de poner un operador para renovacion de tarjetas
def buscar_operador(request):
    if request.is_ajax():
        # operadores = Operador_Nuevo.objects.filter( nombre__icontains = request.GET['name']).values('id', 'razon_social', 'nombre')
        operadores = Operador_Nuevo.objects.filter(es_nuevo=False, nombre__icontains = request.GET['name']).values('id', 'nombre')[:10]
        if len(operadores) == 0:
            return HttpResponse(
                json.dumps([
                    {
                        'id': 'X',
                        'razon_social': '',
                        'nombre': 'No se encontro coincidencias',
                    },
                ]),
                content_type = 'application/json'
            )
        return HttpResponse(json.dumps(list(operadores)), content_type='application/json')
    else:
        return HttpResponse("Esta url solo admite peticiones Ajax")
# fin intento
class SelectOperadores(ListView):
    model = Operador_Nuevo
    template_name = 'tecnico/lista_operadores.html'
    
    def get_context_data(self, *args, **kwargs):
        context = super(SelectOperadores, self).get_context_data(*args, **kwargs)
        operadores = Operador_Nuevo.objects.filter(es_nuevo=False)
        context['operadores'] = operadores
        return context

# Esta clase es para seleccionar al operador que necesita hacer la renovacion de tarjetas
@method_decorator(permission_required('tecnico.verificar'), name='dispatch') 
class RenovarTarjetas(UpdateView):
    model = Operador_Nuevo
    template_name = ''
    form_class = OperarioRenovarForm
    def form_valid(self, form):
        operador = Operador_Nuevo.objects.get(id=self.object.id)
        operador.en_tramite = True
        operador.renovando = True
        operador.save()
        return HttpResponseRedirect(reverse_lazy('tecnico:operador_renovavion_listar'))

@method_decorator(permission_required('tecnico.verificar'), name='dispatch') 
class NotaRenovacion(CreateView):
    model = Nota
    template_name = 'tecnico/nota_renovacion.html'
    form_class = NotaForm
    def form_valid(self, form):
        self.object = form.save(commit = False)
        operador = Operador_Nuevo.objects.get(id=self.kwargs['pk'])
        self.object.operador_n = operador
        self.object.save()
        # return HttpResponseRedirect(reverse_lazy('tecnico:operario_detalle', kwargs = {
        #     'pk': self.object.operador_n.id
        # }))
        return HttpResponseRedirect(reverse_lazy('tecnico:operador_renovavion_listar'))

@method_decorator(permission_required('tecnico.verificar'), name='dispatch') 
class NotaEditRenovacion(UpdateView):
    model = Nota
    template_name = 'tecnico/nota_renovacion.html'
    form_class = NotaForm

    def form_valid(self, form):
        operador = Operador_Nuevo.objects.get(id=self.kwargs['fk'])
        print('-------------'+ str(operador))
        self.object = form.save(commit = False)
        self.object.operador_n = operador
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('tecnico:operador_renovavion_listar'))

# Esta clase permite asignar vehiculos que decean renovar las tarjetas
@method_decorator(permission_required('tecnico.verificar'), name='dispatch') 
class AsignarVehiculosRenovacion(DetailView):
    model = Operador_Nuevo
    template_name = 'tecnico/asignar_renovacion_vehiculos.html'
    def get_context_data(self, *args, **kwargs):
        context = super(AsignarVehiculosRenovacion, self).get_context_data(*args, **kwargs)
        vehiculos = Vehiculo_Nuevo.objects.filter(operador_id = self.kwargs['pk'], es_nuevo=False)
        context['vehiculos'] = vehiculos
    
        vehiculos_renovando = Vehiculo_Nuevo.objects.filter(Q(operador_id = self.kwargs['pk'], renovando=True, es_nuevo=False ) | Q(operador_id = self.kwargs['pk'], renovando=False, es_nuevo=True ))
        context['vehiculos_renovando'] = vehiculos_renovando
        context['formulario'] = FotoVehiculoForm()

        #Algoritmo para controlar los vehiculos inservados el la nota y en la verificacion
        contar_vehi = Nota.objects.get(operador_n= self.kwargs['pk'], fenecio=False)
        try:
            cont = contar_vehi.cantidad_tarjetas
        except:
            cont = 10
        print('-----------jjjjjjjjjjj'+str(cont))
        vehiculos_registrados = Vehiculo_Nuevo.objects.filter(Q(operador = self.object, renovando=True) | Q(operador = self.object, renovando=False, es_nuevo=True))
        print ('//////////' + str(len(vehiculos_registrados)))
        if cont == len(vehiculos_registrados):
            prueba = False
        else:
            prueba = True
        context['prueba'] = prueba
        return context

class SeleccionarVehiculoRenovacion(UpdateView):
    model = Vehiculo_Nuevo
    template_name = ''
    form_class = VehiculoRenovForm
    def form_valid(self, form):
        vehiculo = Vehiculo_Nuevo.objects.get(id=self.object.id)
        vehiculo.renovando = True
        vehiculo.save()
        operador = Operador_Nuevo.objects.get(id=vehiculo.operador_id)
        return HttpResponseRedirect(reverse_lazy('tecnico:operador_renovacion', kwargs = {
            'pk': operador.id
        }))

class QuitarVehiculoRenovacion(UpdateView):
    model = Vehiculo_Nuevo
    template_name = ''
    form_class = VehiculoRenovForm
    def form_valid(self, form):
        vehiculo = Vehiculo_Nuevo.objects.get(id=self.object.id)
        vehiculo.renovando = False
        vehiculo.save()
        operador = Operador_Nuevo.objects.get(id=vehiculo.operador_id)
        return HttpResponseRedirect(reverse_lazy('tecnico:operador_renovacion', kwargs = {
            'pk': operador.id
        }))

@method_decorator(permission_required('tecnico.verificar'), name='dispatch') 
class DetalleOperadorRenovacion(DetailView):
    model = Operador_Nuevo
    # template_name = 'tecnico/operario_verificar.html'
    template_name = 'tecnico/operador_verificacion_detalle.html'
    def get_context_data(self, *args, **kwargs):
        context = super(DetalleOperadorRenovacion, self).get_context_data(*args, **kwargs)

        vehiculosRenovacion = Vehiculo_Nuevo.objects.filter(Q(operador = self.object, renovando=True) | Q(operador = self.object, renovando=False, es_nuevo=True))
        print ('gggggggggggggggggggg--------'+str(len(vehiculosRenovacion)))
        context['vehiculosOp'] = vehiculosRenovacion
        return context

@method_decorator(permission_required('tecnico.verificar'), name='dispatch') 
class VerificarVehiculoRenovacion(DetailView):
    model = Vehiculo_Nuevo
    template_name = 'tecnico/vehiculo_renovando_verificar.html'
    def get_context_data(self, *args, **kwargs):
        context = super(VerificarVehiculoRenovacion, self).get_context_data(*args, **kwargs)
        requisitos_tipo = requisitos_vehiculo_tipo.objects.filter(tipo_vehiculo = self.object.tipo).order_by('id')
        # print ('/***********' + str(requisitos_tipo))
        lista = []
        for a in requisitos_tipo:
            lista.append(a.requisitos_vehi.id)
        # print ('/***********' + str(lista))
        requisitos_v = Requisitos_Vehi.objects.filter(id__in = lista)
        if not Checklist_Vehiculo.objects.filter(vehiculo_nuevo=self.object, vigente=True).exists():    
            for b in requisitos_v:
                p = Checklist_Vehiculo.objects.create(requisitos=b, vehiculo_nuevo=self.object)
        context['checklistvehiculos'] = Checklist_Vehiculo.objects.filter(vehiculo_nuevo= self.object, vigente=True)
        return context

@method_decorator(permission_required('tecnico.verificar'), name='dispatch') 
class CreateInformeRenovacion(CreateView):
    model = Informe
    template_name = 'tecnico/informe_form_renovando.html'
    form_class = InformeForm

    def get_context_data(self, *args, **kwargs):
        context = super(CreateInformeRenovacion, self).get_context_data(*args, **kwargs)
        tipo = self.kwargs['tip']
        if tipo == '3':
            analisis = True
            context['analisis']=analisis
        return context

    def form_valid(self, form):
        self.object = form.save(commit = False)
        operador = Operador_Nuevo.objects.get(id=self.kwargs['pk'])
        self.object.operador = operador
        tipo = self.kwargs['tip']
        if tipo == '1':
            self.object.tipo = 'OBSERVACION'
            self.object.save()
            return HttpResponseRedirect(reverse_lazy('tecnico:informe_obs_renovando', kwargs = {'pk': self.kwargs['pk']}))
        elif tipo == '2':
            self.object.tipo = 'DEVOLUCION'
            self.object.save()
            operador.en_tramite = False
            operador.save()
            nota = Nota.objects.get(operador_n=operador.id, fenecio=False)
            nota.devuelto = True
            nota.save()
            return HttpResponseRedirect(reverse_lazy('tecnico:informe_devol_renovando', kwargs = {'pk': self.kwargs['pk']}))
        elif tipo == '3':
            self.object.tipo = 'INFORME_TECNICO'
            self.object.save()
            return HttpResponseRedirect(reverse_lazy('tecnico:operador_renovavion_listar'))

class informeObsRenovando(View):
    def encabezado_pie(self, pdf, document):
        pdf.saveState()
        logo_gober = settings.MEDIA_ROOT+'/informes/logo7.png'
        logo_transporte = settings.MEDIA_ROOT+'/informes/logo_transporte.jpg'
        #Definimos el tamaño de la imagen a cargar y las coordenadas correspondientes
        pdf.drawImage(logo_gober, 100, 680, 60, 60,preserveAspectRatio=True)
        pdf.drawImage(logo_transporte, 450, 690, 80, 50)
        #Establecemos el tamaño de letra en 16 y el tipo de letra Helvetica
        pdf.setFont("Times-BoldItalic", 12)
        #Dibujamos una cadena en la ubicación X,Y especificada
        pdf.drawString(190, 720, u"Gobierno Autónomo Departamental de Potosí")
        pdf.setFont("Times-BoldItalic", 12)
        pdf.drawString(220, 700, u"Dirección Jurídica Departamental")
        pdf.setFont("Times-Roman", 8.5)
        pdf.drawString(440, 680, u"UNIDAD DE TRANSPORTE")
        logo_dakar = settings.MEDIA_ROOT+'/informes/logo_dakar.jpg'
        logo_banderas = settings.MEDIA_ROOT+'/informes/logo_banderas_pb.png'
        #Definimos el tamaño de la imagen a cargar y las coordenadas correspondientes
        pdf.drawImage(logo_dakar, 100, 10, 60, 50)
        pdf.drawImage(logo_banderas, 180, 12, 250, 15, mask='auto')
        pdf.roundRect(450, 10, 100, 40, 5, stroke = 1)
        pdf.setFont("Times-Roman", 6)
        pdf.drawString(476, 40, u"Dirección Jurídica")
        pdf.drawString(460, 33, u"Plaza de Armas 10 de Noviembre")
        pdf.drawString(476, 26, u"Teléfono 62 29292")
        pdf.drawString(483, 19, u"Fax 6227477")
        pdf.restoreState()

    def informe_obs(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "informe_obs",  alignment=TA_RIGHT, fontSize=10, fontName="Times-Roman"))
        informe = Informe.objects.get(operador=operador.id, tipo='OBSERVACION', vegente=True)
        text = 'Potosí, {}'.format(informe.fecha)
        para = Paragraph(text, styles["informe_obs"] )
        floables.append(para)
        text = 'Cite ADM/URRT/DJD Nº {}/{}'.format(informe.cite, informe.fecha.year)
        para = Paragraph(text, styles["informe_obs"] )
        floables.append(para)

    def dirigido(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "dirigido",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman"))
        floables.append(spacer)
        text = 'Señor:'
        para = Paragraph(text, styles["dirigido"] )
        floables.append(para)
        nota = Nota.objects.get(operador_n=operador.id)
        text = '{}.'.format(nota.representante_ente)
        para = Paragraph(text, styles["dirigido"] )
        floables.append(para)
        text = '{} DEL(LA) {}.'.format(nota.cargo_repr.upper(), nota.nombre_ente.upper())
        para = Paragraph(text, styles["dirigido"] )
        floables.append(para)
    
    def referencia(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "ref",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman"))
        floables.append(spacer)
        text = 'Presente.-'
        para = Paragraph(text, styles["ref"] )
        floables.append(para)
        razon_s = Razon_Social.objects.get(id=operador.id)
        if razon_s.id == 1:
            text = 'Ref.: DOCUMENTOS OBSERVADOS DEL {}'.format(operador.nombre.upper())
        else:
            text = 'Ref.: DOCUMENTOS OBSERVADOS DE LA {}'.format(operador.nombre.upper())
        para = Paragraph(text, styles["ref"] )
        floables.append(para)

    def inicio_carta(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "inicio",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman"))
        nota = Nota.objects.get(operador_n=operador.id, fenecio=False)
        floables.append(spacer)
        text = 'De mi mayor consideración:'
        para = Paragraph(text, styles["inicio"] )
        floables.append(para)
        floables.append(spacer)
        text = '''La Unidad de Registro y Regulación de Transporte dependiente de la Dirección Jurídica del Gobierno Autónomo Departamental de Potosí, ha recibido lo siguiente: la nota del {} con Cite Nº {}/{} del {} afiliados a la {}, donde se solicita tramite de Tarjetas de Operación por lo que se tiene las siguientes observaciones:
        '''.format(
            nota.fecha,
            nota.cite,
            nota.fecha.year,
            operador.nombre,
            nota.nombre_ente
        )
        para = Paragraph(text, styles["inicio"] )
        floables.append(para)        

    def obs_vehiculos(self, floables, spacer, styles, operador, vehi_obs_ids):
        styles.add(ParagraphStyle(name = "obs_vehi",  alignment=TA_LEFT, fontSize=10, fontName="Times-Roman"))
        styles.add(ParagraphStyle(name = "obs_vehi_title",  alignment=TA_CENTER, fontSize=10, fontName="Times-Roman"))
        floables.append(spacer)
        text = 'PARQUE AUTOMOTOR OBSERVADO'
        para = Paragraph(text, styles["obs_vehi_title"] )
        floables.append(para)
        floables.append(spacer)
        vehiculos_obs = Vehiculo_Nuevo.objects.filter(id__in=vehi_obs_ids)
        print('.--.-.-.-.-------'+ str(vehiculos_obs))
        
        encabezado_tabla=['No.', 'Nombre y apellido', 'Placa', 'Observaciones']
        data = [encabezado_tabla]
        num = 1
        for vehiculo in vehiculos_obs:
            observaciones = Checklist_Vehiculo.objects.filter(vehiculo_nuevo=vehiculo.id, cumple=False, vegente=True)
            fila = []
            fila.append(Paragraph(str(num), styles["obs_vehi"]))
            fila.append(Paragraph(vehiculo.propietario, styles["obs_vehi"]))
            fila.append(Paragraph(vehiculo.placa, styles["obs_vehi"]))
            textobs2 = ''
            for observacion in observaciones:
                textobs2 += str(observacion.observacion) + ', '
            fila.append(Paragraph(textobs2, styles["obs_vehi"]))
            data.append(fila)
            num += 1
        print('++++++++****'+ str(data))

        tabla = Table(data = data, style = [('GRID',(0,0),(-1,-1),0.5,colors.grey),], colWidths=[22,150,60,210] )
        floables.append(tabla)

    def fin_carta(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "fin",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman"))
        floables.append(spacer)
        text = '''Es en este sentido que el {}, no cumplen los requisitos exigidos por la Unidad de Transporte segun el Reglameto de Transporte Interprovincial e Intermunicipal de carga y/o pasajeros del Departamento de Potosí para trámite de tarjetas de operaciones teniendo un lapso de cinco días hábiles desde la recepción de la presente para subsanar, caso contrario se efectuará la devolución de la documentación.'''.format(operador.nombre)

        para = Paragraph(text, styles["fin"] )
        floables.append(para)

    def firma(self, floables, spacer, styles):
        styles.add(ParagraphStyle(name = "firma",  alignment=TA_CENTER, fontSize=10, fontName="Times-Roman"))
        floables.append(spacer)
        floables.append(spacer)
        floables.append(spacer)
        floables.append(spacer)
        floables.append(spacer)
        text = '''Lic. Lourdes Arce Quispe'''
        para = Paragraph(text, styles["firma"] )
        floables.append(para)
        text = '''TECNICO II UNIDAD DE REGISTRO Y REGULACION DE TRANSPORTE'''
        para = Paragraph(text, styles["firma"] )
        floables.append(para)

    def get(self, request, *args, **kwargs):
        #Indicamos el tipo de contenido a devolver, en este caso un pdf
        response = HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename="First-PDF.pdf"'
        #La clase io.BytesIO permite tratar un array de bytes como un fichero binario, se utiliza como almacenamiento temporal
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize= letter,
                                rightMargin = 63,
                                leftMargin = 100,
                                topMargin = 115,
                                bottomMagin= 48,
                                showBoundary = False)
        styles = getSampleStyleSheet()
        flowables = []
        spacer = Spacer(1, 0.25*inch)
        # Obtener al operador
        operador = Operador_Nuevo.objects.get(id=self.kwargs['pk'])
        # Que vehiculos estan observados
        vehiculos = Vehiculo_Nuevo.objects.filter(operador=operador.id, renovando=True)
        vehi_obs_ids = []
        for vehiculo in vehiculos:
            # if Checklist_Vehiculo.objects.filter(vehiculo_nuevo__in=vehiculo, cumple= False).exists():
            if Checklist_Vehiculo.objects.filter(vehiculo_nuevo=vehiculo.id, cumple=False, vegente=True).exists():
                vehi_obs_ids.append(vehiculo.id)
        print('222222222222'+str(vehi_obs_ids))

        self.informe_obs(flowables, spacer, styles, operador)
        self.dirigido(flowables, spacer, styles, operador)
        self.referencia(flowables, spacer, styles, operador)
        self.inicio_carta(flowables, spacer, styles, operador)
        # self.obs_operador(flowables, spacer, styles, operador)
        if vehi_obs_ids != []:
            self.obs_vehiculos(flowables, spacer, styles, operador, vehi_obs_ids)
        self.fin_carta(flowables, spacer, styles, operador)
        self.firma(flowables, spacer, styles)

        doc.build(flowables, onFirstPage=self.encabezado_pie, onLaterPages=self.encabezado_pie)
        response.write(buffer.getvalue())
        buffer.close()
        return response

class informeDevol_renovacion(View):
    def encabezado_pie(self, pdf, document):
        pdf.saveState()
        logo_gober = settings.MEDIA_ROOT+'/informes/logo7.png'
        logo_transporte = settings.MEDIA_ROOT+'/informes/logo_transporte.jpg'
        #Definimos el tamaño de la imagen a cargar y las coordenadas correspondientes
        pdf.drawImage(logo_gober, 100, 680, 60, 60,preserveAspectRatio=True)
        pdf.drawImage(logo_transporte, 450, 690, 80, 50)
        #Establecemos el tamaño de letra en 16 y el tipo de letra Helvetica
        pdf.setFont("Times-BoldItalic", 12)
        #Dibujamos una cadena en la ubicación X,Y especificada
        pdf.drawString(190, 720, u"Gobierno Autónomo Departamental de Potosí")
        pdf.setFont("Times-BoldItalic", 12)
        pdf.drawString(220, 700, u"Dirección Jurídica Departamental")
        pdf.setFont("Times-Roman", 8.5)
        pdf.drawString(440, 680, u"UNIDAD DE TRANSPORTE")
        logo_dakar = settings.MEDIA_ROOT+'/informes/logo_dakar.jpg'
        logo_banderas = settings.MEDIA_ROOT+'/informes/logo_banderas_pb.png'
        #Definimos el tamaño de la imagen a cargar y las coordenadas correspondientes
        pdf.drawImage(logo_dakar, 100, 10, 60, 50)
        pdf.drawImage(logo_banderas, 180, 12, 250, 15, mask='auto')
        pdf.roundRect(450, 10, 100, 40, 5, stroke = 1)
        pdf.setFont("Times-Roman", 6)
        pdf.drawString(476, 40, u"Dirección Jurídica")
        pdf.drawString(460, 33, u"Plaza de Armas 10 de Noviembre")
        pdf.drawString(476, 26, u"Teléfono 62 29292")
        pdf.drawString(483, 19, u"Fax 6227477")
        pdf.restoreState()

    def informe_devol(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "informe_devol",  alignment=TA_RIGHT, fontSize=10, fontName="Times-Roman"))
        informe = Informe.objects.get(operador=operador.id, tipo='DEVOLUCION', vigente=True)
        text = 'Potosí, {}'.format(informe.fecha)
        para = Paragraph(text, styles["informe_devol"] )
        floables.append(para)
        text = 'Cite ADM/URRT/DJD Nº {}/{}'.format(informe.cite, informe.fecha.year)
        para = Paragraph(text, styles["informe_devol"] )
        floables.append(para)
    
    def dirigido(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "dirigido",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman"))
        floables.append(spacer)
        text = 'Señor:'
        para = Paragraph(text, styles["dirigido"] )
        floables.append(para)
        nota = Nota.objects.get(operador_n=operador.id, fenecio=False)
        text = '{}.'.format(nota.representante_ente)
        para = Paragraph(text, styles["dirigido"] )
        floables.append(para)
        text = '{} DEL(LA) {}.'.format(nota.cargo_repr.upper(), nota.nombre_ente.upper())
        para = Paragraph(text, styles["dirigido"] )
        floables.append(para)

    def referencia(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "ref",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman"))
        floables.append(spacer)
        text = 'Presente.-'
        para = Paragraph(text, styles["ref"] )
        floables.append(para)
        razon_s = Razon_Social.objects.get(id=operador.id)
        if razon_s.id == 1:
            text = 'Ref.: DEVOLUCION DE DOCUMENTACION DEL {}'.format(operador.nombre.upper())
        else:
            text = 'Ref.: DEVOLUCION DE DOCUMENTACION DE LA {}'.format(operador.nombre.upper())
        para = Paragraph(text, styles["ref"] )
        floables.append(para)

    def inicio_carta(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "inicio",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman"))
        nota = Nota.objects.get(operador_n=operador.id, fenecio=False)
        floables.append(spacer)
        text = 'De mi mayor consideración:'
        para = Paragraph(text, styles["inicio"] )
        floables.append(para)
        floables.append(spacer)
        text = '''La Unidad de Registro y Regulación de Transporte dependiente de la Dirección Jurídica del Gobierno Autónomo Departamental de Potosí, ha recibido lo siguiente: la nota del {} con Cite Nº {}/{} del {} afiliados a la {}, donde se solicita tramite de Tarjetas de Operación para un total de {} vehículos:
        '''.format(
            nota.fecha,
            nota.cite,
            nota.fecha.year,
            operador.nombre,
            nota.nombre_ente,
            nota.cantidad_tarjetas,
        )
        para = Paragraph(text, styles["inicio"] )
        floables.append(para)
    
    def fin_carta(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "fin",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman"))
        informe_obs = Informe.objects.get(operador=operador.id, tipo='OBSERVACION', vigente=True)
        floables.append(spacer)
        text = '''Es en este sentido que en fecha {} con Cite ADM/URRT/DJD N° {}/{} se efectuó la observación al {} quienes no subsanaron estas observaciones Hasta la fecha..'''.format(
            informe_obs.fecha,
            informe_obs.cite,
            informe_obs.fecha.year,
            operador.nombre,
            )
        para = Paragraph(text, styles["fin"] )
        floables.append(para)
        text = '''Teniendo estos antecedentes, se efectúa la devolución de la documentación de la documentación presentada por que no cumple con los requisitos del Reglamento de Transporte Interprovincial e Intermunicipal de Carga y/o Pasajeros del Departamento de Potosí'''
        para = Paragraph(text, styles["fin"] )
        floables.append(para)
        floables.append(spacer)
        text = '''Sin otro particulaer motivo, me despido con las consideraciones más distinguidas'''
        para = Paragraph(text, styles["fin"] )
        floables.append(para)

    def firma(self, floables, spacer, styles):
        styles.add(ParagraphStyle(name = "firma",  alignment=TA_CENTER, fontSize=10, fontName="Times-Roman"))
        floables.append(spacer)
        floables.append(spacer)
        floables.append(spacer)
        floables.append(spacer)
        floables.append(spacer)
        text = '''Lic. Lourdes Arce Quispe'''
        para = Paragraph(text, styles["firma"] )
        floables.append(para)
        text = '''TECNICO II UNIDAD DE REGISTRO Y REGULACION DE TRANSPORTE'''
        para = Paragraph(text, styles["firma"] )
        floables.append(para)

    def get(self, request, *args, **kwargs):
        #Indicamos el tipo de contenido a devolver, en este caso un pdf
        response = HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename="First-PDF.pdf"'
        #La clase io.BytesIO permite tratar un array de bytes como un fichero binario, se utiliza como almacenamiento temporal
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize= letter,
                                rightMargin = 63,
                                leftMargin = 100,
                                topMargin = 115,
                                bottomMagin= 48,
                                showBoundary = False)
        styles = getSampleStyleSheet()
        flowables = []
        spacer = Spacer(1, 0.25*inch)
        # Obtener al operador
        operador = Operador_Nuevo.objects.get(id=self.kwargs['pk'])
        # Que vehiculos estan observados
        vehiculos = Vehiculo_Nuevo.objects.filter(operador=operador.id, renovando=True)
        vehi_obs_ids = []
        self.informe_devol(flowables, spacer, styles, operador)
        self.dirigido(flowables, spacer, styles, operador)
        self.referencia(flowables, spacer, styles, operador)
        self.inicio_carta(flowables, spacer, styles, operador)
        self.fin_carta(flowables, spacer, styles, operador)
        self.firma(flowables, spacer, styles)
        doc.build(flowables, onFirstPage=self.encabezado_pie, onLaterPages=self.encabezado_pie)
        response.write(buffer.getvalue())
        buffer.close()
        return response

class informeTecnico_renovacion(View):
    def encabezado_pie(self, pdf, document):
        pdf.saveState()
        logo_gober = settings.MEDIA_ROOT+'/informes/logo7.png'
        logo_transporte = settings.MEDIA_ROOT+'/informes/logo_transporte.jpg'
        #Definimos el tamaño de la imagen a cargar y las coordenadas correspondientes
        pdf.drawImage(logo_gober, 100, 680, 60, 60,preserveAspectRatio=True)
        pdf.drawImage(logo_transporte, 450, 690, 80, 50)
        #Establecemos el tamaño de letra en 16 y el tipo de letra Helvetica
        pdf.setFont("Times-BoldItalic", 12)
        #Dibujamos una cadena en la ubicación X,Y especificada
        pdf.drawString(190, 720, u"Gobierno Autónomo Departamental de Potosí")
        pdf.setFont("Times-BoldItalic", 12)
        pdf.drawString(220, 700, u"Dirección Jurídica Departamental")
        pdf.setFont("Times-Roman", 8.5)
        pdf.drawString(440, 680, u"UNIDAD DE TRANSPORTE")
        logo_dakar = settings.MEDIA_ROOT+'/informes/logo_dakar.jpg'
        logo_banderas = settings.MEDIA_ROOT+'/informes/logo_banderas_pb.png'
        #Definimos el tamaño de la imagen a cargar y las coordenadas correspondientes
        pdf.drawImage(logo_dakar, 100, 10, 60, 50)
        pdf.drawImage(logo_banderas, 180, 12, 250, 15, mask='auto')
        pdf.roundRect(450, 10, 100, 40, 5, stroke = 1)
        pdf.setFont("Times-Roman", 6)
        pdf.drawString(476, 40, u"Dirección Jurídica")
        pdf.drawString(460, 33, u"Plaza de Armas 10 de Noviembre")
        pdf.drawString(476, 26, u"Teléfono 62 29292")
        pdf.drawString(483, 19, u"Fax 6227477")
        pdf.restoreState()

    def informe_tecnico(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "informe_tecnico",  alignment=TA_CENTER, fontSize=13, fontName="Times-Bold"))
        informe = Informe.objects.get(operador=operador.id, tipo='INFORME_TECNICO', vigente=True)
        text = 'INFORME TÉCNICO'
        para = Paragraph(text, styles["informe_tecnico"])
        floables.append(para)
        text = 'URRT Nº {}/{}'.format(informe.cite, informe.fecha.year)
        para = Paragraph(text, styles["informe_tecnico"])
        floables.append(para)
    
    def dirigido(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "dirigido_a",  alignment=TA_LEFT, bulletIndent=20, fontSize=10, fontName="Times-Roman"))
        styles.add(ParagraphStyle(name = "dirigido_d",  alignment=TA_LEFT, bulletIndent=20, fontSize=10, fontName="Times-Roman"))
        styles.add(ParagraphStyle(name = "dirigido_r",  alignment=TA_LEFT, bulletIndent=20, fontSize=10, fontName="Times-Roman"))
        styles.add(ParagraphStyle(name = "dirigido_f",  alignment=TA_LEFT, bulletIndent=20, fontSize=10, fontName="Times-Roman"))
        styles.add(ParagraphStyle(name = "dirigido_bold",  alignment=TA_LEFT, fontSize=10, fontName="Times-Bold"))
        styles.add(ParagraphStyle(name = "dirigido_bold1",  alignment=TA_LEFT, fontSize=8, fontName="Times-Bold"))
        


        floables.append(spacer)

        data = []
        fila = []
        fila.append(Paragraph('<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; A:</p>', styles["dirigido_a"]))
        fila.append(Paragraph('Dr. Wilson Condori López', styles["dirigido_a"]))
        data.append(fila)
        fila = []
        fila.append(Paragraph('', styles["dirigido_a"]))
        fila.append(Paragraph('<strong>RESPONSABLE UNIDAD DE REGISTRO Y REGULACIÓN DE TRANSPORTE</strong>', styles["dirigido_a"]))
        data.append(fila)
        fila = []
        fila.append(Paragraph('', styles["dirigido_a"]))
        fila.append(Paragraph('', styles["dirigido_a"]))
        data.append(fila)
        fila = []
        fila.append(Paragraph('<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; DE:</p>', styles["dirigido_a"]))
        fila.append(Paragraph('Lic. Lourdes Arce Quispe', styles["dirigido_a"]))
        data.append(fila)
        fila = []
        fila.append(Paragraph('', styles["dirigido_a"]))
        fila.append(Paragraph('<strong>TÉCNICO II UNIDAD DE REGISTRO Y REGULACIÓN DE TRANSPORTE</strong>', styles["dirigido_a"]))
        data.append(fila)
        fila = []
        fila.append(Paragraph('', styles["dirigido_a"]))
        fila.append(Paragraph('', styles["dirigido_a"]))
        data.append(fila)
        fila = []
        fila.append(Paragraph('<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; REF.:</p>', styles["dirigido_a"]))
        if operador.razon_social_id == 1:
            text = '<strong>SOLICITUD DE TARJETAS DE OPERACIÓN A FAVOR DEL {}</strong>'.format(operador.nombre.upper())
        else:
            text = '<strong>SOLICITUD DE TARJETAS DE OPERACIÓN A FAVOR DE LA {}</strong>'.format(operador.nombre.upper())
        # text.encode('utf-16')
        fila.append(Paragraph(smart_str(text), styles["dirigido_a"]))
        data.append(fila)
        fila = []
        fila.append(Paragraph('', styles["dirigido_a"]))
        fila.append(Paragraph('', styles["dirigido_a"]))
        data.append(fila)

        informe = Informe.objects.get(operador=operador.id, tipo='INFORME_TECNICO', vigente=True)
        # Convertir la fecha a literal
        fecha = informe.fecha

        dia = str(fecha.day)
        if dia == '1':
            dia = '01'
        elif dia == '2':
            dia = '02'
        elif dia == '3':
            dia = '03'
        elif dia == '4':
            dia = '04'
        elif dia == '5':
            dia = '05'
        elif dia == '6':
            dia = '06'
        elif dia == '7':
            dia = '07'
        elif dia == '8':
            dia = '08'
        elif dia == '9':
            dia = '09'
        mes = str(fecha.month)
        if mes == '1':
            mes = 'enero'
        elif mes == '2':
            mes = 'febrero'
        elif mes == '3':
            mes = 'marzo'
        elif mes == '4':
            mes = 'abril'
        elif mes == '5':
            mes = 'mayo'
        elif mes == '6':
            mes = 'junio'
        elif mes == '7':
            mes = 'julio'
        elif mes == '8':
            mes = 'agosto'
        elif mes == '9':
            mes = 'septiembre'
        elif mes == '10':
            mes = 'octubre'
        elif mes == '11':
            mes = 'noviembre'
        elif mes == '12':
            mes = 'diciembre'

        anio = str(fecha.year)

        fila = []
        fila.append(Paragraph('<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; FECHA:</p>', styles["dirigido_a"]))
        fila.append(Paragraph('Potosí, {} de {} de {}'.format(dia, mes, anio), styles["dirigido_a"]))
        data.append(fila)

        tabla = Table(data = data, style = [('VALIGN',(0,6),(0,6),'TOP'),], colWidths=[70,370], rowHeights=[15,15,30,15,15,30,30,30,5] )
        # tabla = Table(data = data, style = [('BOX',(0,0),(-1,-1),0.5,colors.grey),])
        floables.append(tabla)



        # floables.append(spacer)
        # text = '<bullet>A:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</bullet>Dr. Wilson Condori López'
        # print(text)
        # para = Paragraph(text, styles["dirigido_a"] )
        # floables.append(para)
        # text = '<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</p>RESPONSABLE UNIDAD DE REGISTRO Y REGULACION DE TRANSPORTE'
        # para = Paragraph(text, styles["dirigido_bold"] )
        # floables.append(para)
        # floables.append(spacer)
        # text = '<bullet>De:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</bullet>Lic. Lourdes Arce Quispe'
        # para = Paragraph(text, styles["dirigido_d"] )
        # floables.append(para)
        # text = '<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</p>TECNICO II UNIDAD DE REGISTRO Y REGULACION DE TRANSPORTE'
        # para = Paragraph(text, styles["dirigido_bold"] )
        # floables.append(para)
        # floables.append(spacer)
        # if operador.razon_social_id == 1:
        #     text = '<bullet>Ref.:&nbsp;&nbsp;&nbsp;&nbsp;</bullet><strong>SOLICITUD DE TARJETAS DE OPERACION A FAVOR DEL</strong>'
        # else:
        #     text = '<bullet>Ref.:&nbsp;&nbsp;&nbsp;&nbsp;</bullet><strong>SOLICITUD DE TARJETAS DE OPERACION A FAVOR DE LA</strong>'
        # para = Paragraph(text, styles["dirigido_r"] )
        # floables.append(para)
        # text = '<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</p>{}'.format(operador.nombre.upper())
        # para = Paragraph(text, styles["dirigido_bold1"] )
        # floables.append(para)
        # floables.append(spacer)
        # informe = Informe.objects.get(operador=operador.id, tipo='INFORME_TECNICO', vigente=True)
        # mes=informe.fecha.month

        # if mes == 1:
        #     mes = "enero"
        # elif mes == 2:
        #     mes = "febrero"
        # elif mes == 3:
        #     mes = "marzo"
        # elif mes == 4:
        #     mes = "abril"
        # elif mes == 5:
        #     mes = "mayo"
        # elif mes == 6:
        #     mes = "junio"
        # elif mes == 7:
        #     mes = "julio"
        # elif mes == 8:
        #     mes = "agosto"
        # elif mes == 9:
        #     mes = "septiembre"
        # elif mes == 10:
        #     mes = "octubre"
        # elif mes == 11:
        #     mes = "noviembre"
        # elif mes == 12:
        #     mes = "diciembre"
        # text = '<bullet>Fecha:&nbsp;&nbsp;</bullet>Potosí, {} de {} de {}'.format(informe.fecha.day, mes, informe.fecha.year)
        # para = Paragraph(text, styles["dirigido_a"] )
        # floables.append(para)
        # floables.append(spacer)
        # floables.append(spacer)
        text = '_______________________________________________________________________________________'
        para = Paragraph(text, styles["dirigido_a"] )
        floables.append(para)

    def antecedentes(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "antec",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman"))
        styles.add(ParagraphStyle(name = "antec_bold",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Bold"))
        styles.add(ParagraphStyle(name = "center",  alignment=TA_CENTER, fontSize=10, fontName="Times-Bold"))
        styles.add(ParagraphStyle(name = "antc_bullet",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman"),alias='ul')
        styles.add(ParagraphStyle(name = "antc_bullet_1",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman", bulletText="-"),alias='cl')
        nota = Nota.objects.get(operador_n=operador.id, fenecio=False)
        floables.append(spacer)
        text = 'I ANTECEDENTES.'
        para = Paragraph(text, styles["antec_bold"] )
        floables.append(para)
        floables.append(Spacer(0.5,0.1*inch))
        if operador.es_nuevo == True:
            if operador.razon_social_id == 1:
                text = 'El {}, en representación del {} mediante Nota con Cite N° {}/{} solicita Tarjetas de Operación, presentando la documentación correspondiente y exigida por la Unidad de Transporte según el Reglamento de Transporte Interprovincial e Intermunicipal de carga y/o pasajeros del Departamento de Potosí:'.format(
                    nota.nombre_ente, 
                    operador.nombre.upper(),
                    nota.cite,
                    nota.fecha.year,
                    )
            else:
                text = 'La {}, en representación de la {} mediante Nota con Cite N° {}/{} solicita Tarjetas de Operación, presentando la documentación correspondiente y exigida por la Unidad de Transporte según el Reglamento de Transporte Interprovincial e Intermunicipal de carga y/o pasajeros del Departamento de Potosí:'.format(
                    nota.nombre_ente, 
                    operador.nombre.upper(),
                    nota.cite,
                    nota.fecha.year,
                   )
            para = Paragraph(text, styles["antec"] )
            floables.append(para)
        else:
            if operador.razon_social_id == 1:
                text = 'El {} en representación del {} mediante Cite N° {}/{} solicita la renovación de Tarjetas de Operación para su parque automotor, presentando la documentacion correspondiente y exigida por la Unidad de Transporte según el Reglamento de Transporte Interprovincial e Intermunicipal de carga y/o pasajeros del Departamento de Potosí:'.format(
                    nota.nombre_ente,
                    operador.nombre,
                    nota.cite,
                    nota.fecha.year,
                    )
            else:
                text = 'La {} en representación de la {} mediante Cite N° {}/{} solicita la renovación de Tarjetas de Operación para su parque automotor, presentando la documentacion correspondiente y exigida por la Unidad de Transporte según el Reglamento de Transporte Interprovincial eIntermunicipal de carga y/o pasajeros del Departamento de Potosí:'.format(
                    nota.nombre_ente,
                    operador.nombre,
                    nota.cite,
                    nota.fecha.year,
                    )
            para = Paragraph(text, styles["antec"])
            floables.append(para)
        if operador.es_nuevo == True:
            rs = Razon_Social.objects.get(nombre = operador.razon_social)
            print('-c-c-c-c-c-c-c'+str(rs))
            queryset_requisitos = requisitos_razon_social.objects.filter(razon_social = rs).order_by('id')
            print('-c-c-c-c-c-c-c'+str(queryset_requisitos))
            lista = []
            for a in queryset_requisitos:
                lista.append(a.requisitos_rs.id)
                print ('//////////------' + str(lista))
            requisitos = Requisitos_RS.objects.filter(id__in=lista)
            print ('//////////------' + str(requisitos))
            if requisitos:
                text = 'REQUISITOS DEL OPERADOR'
                para = Paragraph(text, styles["center"])
                floables.append(para)
                floables.append(Spacer(1, 10))

            for requisito in requisitos:
                text = '<bullet>&#9679; &nbsp;&nbsp;</bullet>{}'.format(requisito)
                para = Paragraph(text, styles["antc_bullet"])
                floables.append(para)
                floables.append(Spacer(1, 10))
            
            floables.append(spacer)
            requisitos_vehiculos = Requisitos_Vehi.objects.exclude(id=7)
            print ('//////////------' + str(requisitos_vehiculos))
            for requisito in requisitos_vehiculos:
                text = '{}'.format(requisito.descripcion)
                para = Paragraph(text, styles["antc_bullet_1"])
                floables.append(para)
                floables.append(Spacer(1, 10))

    def analisis_tecnico(self, floables, spacer, styles, operador):
        styles.add(ParagraphStyle(name = "analisis",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman"))
        styles.add(ParagraphStyle(name = "analisis_bold",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Bold"))
        styles.add(ParagraphStyle(name = "analisis_center_bold",  alignment=TA_CENTER, fontSize=10, fontName="Times-Bold"))
        styles.add(ParagraphStyle(name = "analisis_left_bold",  alignment=TA_LEFT, fontSize=10, fontName="Times-Bold"))
        styles.add(ParagraphStyle(name = "analisis_center",  alignment=TA_CENTER, fontSize=10, fontName="Times-Roman"))
        styles.add(ParagraphStyle(name = "analisis_bullet",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman", bulletText="*"))
        floables.append(spacer)
        text = 'II ANÁLISIS TÉCNICO.'
        para = Paragraph(text, styles["analisis_bold"] )
        floables.append(para)
        floables.append(spacer)
        text = 'Revisada la documentación presentada se determina lo siguiente:'
        para = Paragraph(text, styles["analisis"] )
        floables.append(para)
        floables.append(spacer)
        nota = Nota.objects.get(operador_n=operador.id, fenecio=False)
        if operador.razon_social_id == 1:
            text = '1.- La solicitud presentada por el {} ha sido presentada por su Ente Matriz - {}.'.format(
                operador.nombre,
                nota.nombre_ente,
           )
        else:
            text = '1.- La solicitud presentada por la {} ha sido presentada por su Ente Matriz - {}.'.format(
                operador.nombre,
                nota.nombre_ente,
            )
        para = Paragraph(text, styles["analisis"] )
        floables.append(para)
        floables.append(spacer)
        if operador.es_nuevo == True:
            if operador.razon_social_id == 1:
                text = '2.- RUTA SOLICITADA POR EL {}'.format(operador.nombre.upper())
            else:
                text = '2.- RUTA SOLICITADA POR LA {}'.format(operador.nombre.upper())
            para = Paragraph(text, styles["analisis_center_bold"] )
            floables.append(para)
            floables.append(spacer)
            text = '{}'.format(nota.ruta_solicitada.upper())
            para = Paragraph(text, styles["analisis_center"] )
            floables.append(para)
            floables.append(spacer)
        else:
            if operador.razon_social_id == 1:
                text = '2.- El {}, tiene la siguiente ruta autorizada:'.format(operador.nombre,)
            else:
                text = '2.- La {}, tiene la siguiente ruta autorizada:'.format(operador.nombre,)
            para = Paragraph(text, styles["analisis"])
            floables.append(para)
            floables.append(spacer)
            if operador.razon_social_id == 1:
                text = 'HORARIO Y RUTA AUTORIZADA DEL {}'.format(operador.nombre.upper())
            else:
                text = 'HORARIO Y RUTA AUTORIZADA DE LA {}'.format(operador.nombre.upper())
            para = Paragraph(text, styles["analisis_center_bold"])
            floables.append(para)
            floables.append(spacer)
            #Poner Ruta Una vez que sea registrado el operador nuevo
 
            rutas = Ruta.objects.filter(operador=operador.id)
            encabezado = ['RUTA', 'HORARIO']
            data = [encabezado]
            for ruta in rutas:
                fila = []
                fila.append(Paragraph(ruta.ruta, styles["analisis"]))
                fila.append(Paragraph(ruta.hora, styles["analisis"]))
                data.append(fila)
                # fila = []
                # fila.append(Paragraph(ruta.ruta_v, styles["analisis"]))
                # fila.append(Paragraph(ruta.hora_v, styles["analisis"]))
                # data.append(fila)
            # tabla = Table(data = data, style = [('GRID',(0,0),(-1,-1),0.5,colors.grey),], colWidths=[22,150,60,210] )
            tabla = Table(data = data, style = [('BOX',(0,0),(-1,-1),0.5,colors.grey),])
            floables.append(tabla)            

            floables.append(spacer)
            if operador.razon_social_id == 1:
                text = '3.- El {} solicitó renovación de Tarjetas de Operación para el siguiente parque automotor:'.format(operador.nombre)
            else:
                text = '3.- La {} solicitó renovación de Tarjetas de Operación para el siguiente parque automotor:'.format(operador.nombre)
            para = Paragraph(text, styles["analisis"])
            floables.append(para)
            floables.append(spacer)
            text = 'PARQUE AUTOMOTOR RENOVACION'
            para = Paragraph(text, styles["analisis_center_bold"] )
            floables.append(para)

            vehiculos = Vehiculo_Nuevo.objects.filter(operador=operador.id, renovando=True)
            encabezado_tabla=['No.', 'Nombre y apellido', 'Placa']
            data = [encabezado_tabla]
            num = 1
            for vehiculo in vehiculos:
                fila = []
                fila.append(Paragraph(str(num), styles["analisis"]))
                fila.append(Paragraph(vehiculo.propietario, styles["analisis"]))
                fila.append(Paragraph(vehiculo.placa, styles["analisis"]))
                data.append(fila)
                num += 1
            tabla = Table(data = data, style = [('GRID',(0,0),(-1,-1),0.5,colors.grey),], colWidths=[22,150,60,210] )
            floables.append(tabla)
            floables.append(spacer)

            if Vehiculo_Nuevo.objects.filter(operador=operador.id, es_nuevo=True).exists():
                vehiculos = Vehiculo_Nuevo.objects.filter(operador=operador.id, es_nuevo=True)
                text = 'Tambien se solicitó tarjetas para los sigientes vehículos nuevos.'
                para = Paragraph(text, styles["analisis"] )
                floables.append(para)
                floables.append(spacer)
                text = 'PARQUE AUTOMOTOR NUEVOS'
                para = Paragraph(text, styles["analisis_center_bold"] )
                floables.append(para)
                
                encabezado_tabla=['No.', 'Nombre y apellido', 'Placa']
                data = [encabezado_tabla]
                num = 1
                for vehiculo in vehiculos:
                    fila = []
                    fila.append(Paragraph(str(num), styles["analisis"]))
                    fila.append(Paragraph(vehiculo.propietario, styles["analisis"]))
                    fila.append(Paragraph(vehiculo.placa, styles["analisis"]))
                    data.append(fila)
                    num += 1
                tabla = Table(data = data, style = [('GRID',(0,0),(-1,-1),0.5,colors.grey),], colWidths=[22,150,60,210] )
                floables.append(tabla)

        floables.append(spacer)
        informe = Informe.objects.get(operador=operador.id, vigente=True)
        text = '4.- {}'.format(informe.ans_tecnico)
        para = Paragraph(text, styles["analisis"])
        floables.append(para)
        floables.append(spacer)

        text = 'III CONCLUSIONES Y RECOMENDACIONES.'
        para = Paragraph(text, styles["analisis_bold"])
        floables.append(para)
        floables.append(spacer)
        text = '{}'.format(informe.concluciones)
        para = Paragraph(text, styles["analisis"])
        floables.append(para)

    def get(self, request, *args, **kwargs):
        #Indicamos el tipo de contenido a devolver, en este caso un pdf
        response = HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename="First-PDF.pdf"'
        #La clase io.BytesIO permite tratar un array de bytes como un fichero binario, se utiliza como almacenamiento temporal
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize= letter,
                                rightMargin = 63,
                                leftMargin = 100,
                                topMargin = 115,
                                bottomMagin= 48,
                                showBoundary = False)
        styles = getSampleStyleSheet()
        flowables = []
        spacer = Spacer(1, 0.25*inch)
        # Obtener al operador
        operador = Operador_Nuevo.objects.get(id=self.kwargs['pk'], vigente=True)
        # Que vehiculos estan observados
        vehiculos = Vehiculo_Nuevo.objects.filter(operador=operador.id)
        vehi_obs_ids = []
        self.informe_tecnico(flowables, spacer, styles, operador)
        self.dirigido(flowables, spacer, styles, operador)
        self.antecedentes(flowables, spacer, styles, operador)
        self.analisis_tecnico(flowables, spacer, styles, operador)
        # self.fin_carta(flowables, spacer, styles, operador)
        # self.firma(flowables, spacer, styles)
        doc.build(flowables, onFirstPage=self.encabezado_pie, onLaterPages=self.encabezado_pie)
        response.write(buffer.getvalue())
        buffer.close()
        return response

# Aumetar registro de vehiculos en una renovacion
@method_decorator(permission_required('tecnico.verificar'), name='dispatch') 
class CreateVehiculoN(CreateView):
    model = Vehiculo_Nuevo
    template_name = 'tecnico/crear_vehiculo_nuevo.html'
    form_class = VehiculoNForm
    
    def form_valid(self, form):
        self.object = form.save(commit = False)
        operador = Operador_Nuevo.objects.get(id=self.kwargs['pk'])
        self.object.operador = operador
        tipo = Tipo_Vehiculo.objects.get(id=1)
        self.object.tipo = tipo
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('tecnico:operador_renovacion', kwargs = {
            'pk': self.object.operador.id
        }))

    def get_initial(self):
        tipo = 1
        operario = self.kwargs['pk']
        return {
            'tipo': tipo,
            'operario': operario,
        }
    
    def get_context_data(self, *args, **kwargs):
        context = super(CreateVehiculoN, self).get_context_data(*args, **kwargs)
        operador = Operador_Nuevo.objects.get(id=self.kwargs['pk'])
        pk = operador.id
        context['llave'] = pk
        return context

@method_decorator(permission_required('tecnico.verificar'), name='dispatch') 
class EditVehiculoN(UpdateView):
    model = Vehiculo_Nuevo
    template_name = 'tecnico/vehiculo_n_form.html'
    form_class = VehiculoForm

    def form_valid(self, form):
        self.object = form.save(commit = False)
        print ('//////////' + str(self.kwargs['fk']))
        print ('//////////' + str(self.kwargs['pk']))
        operador = Operador_Nuevo.objects.get(id=self.kwargs['fk'])
        self.object.operador = operador
        tipo = Tipo_Vehiculo.objects.get(id=1)
        self.object.tipo = tipo
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('tecnico:operador_renovacion', kwargs = {
            'pk': operador.id
        }))

    def get_context_data(self, *args, **kwargs):
        context = super(EditVehiculoN, self).get_context_data(*args, **kwargs)
        context['llave'] = self.kwargs['fk'];
        return context

@method_decorator(permission_required('tecnico.verificar'), name='dispatch') 
class DeleteVehivuloN(DeleteView):
    model = Vehiculo_Nuevo
    template_name = 'tecnico/vehiculo_n_eliminar.html'
    def get_success_url(self, **kwargs):
        return reverse_lazy('tecnico:operador_renovacion', kwargs = {
            'pk': self.kwargs['fk']})

    def get_context_data(self, *args, **kwargs):
        context = super(DeleteVehivuloN, self).get_context_data(*args, **kwargs)
        context['llave'] = self.kwargs['fk'];
        return context

class CrearFoto(CreateView):
    model = Fotos_Vehiculo
    template_name = ''
    form_class = FotoVehiculoForm
    def form_valid(self, form):
        self.object = form.save(commit = False)
        vehiculo = Vehiculo_Nuevo.objects.get(id=self.kwargs['pk'])
        self.object.vehiculo = vehiculo
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('tecnico:operador_renovacion', kwargs = {
            'pk': self.object.vehiculo.operador.id
        }))

class EliminarFoto(DeleteView):
    model = Fotos_Vehiculo
    template_name = 'tecnico/foto_delete.html'
    def get_success_url(self, **kwargs):
        return reverse_lazy('tecnico:operador_renovacion', kwargs = {
            'pk': self.kwargs['fk']})

    def get_context_data(self, *args, **kwargs):
        context = super(EliminarFoto, self).get_context_data(*args, **kwargs)
        context['llave'] = self.kwargs['fk']
        return context

class ListarMarca(ListView):
    model = Marca
    template_name = 'tecnico/listar_marcas.html'
    def get_context_data(self, *args, **kwargs):
        context = super(ListarMarca, self).get_context_data(*args, **kwargs)
        context['formulario'] = MarcaForm()
        return context

class CreateMarca(CreateView):
    model = Marca
    template_name = ''
    form_class = MarcaForm
    success_url = reverse_lazy('tecnico:listar_marca') 

class DeleteMarca(DeleteView):
    model = Marca
    template_name = ''
    success_url = reverse_lazy('tecnico:listar_marca') 