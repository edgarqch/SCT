# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.core.urlresolvers import reverse_lazy
from django.views.generic import View, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.http import HttpResponseRedirect 

# Import your forms here.
from apps.tecnico.form import OperarioNuevoForm, VehiculoNForm, RutaForm
from apps.operario.form import VehiculoForm, OperadorForm, OpRegisterForm, VehiRegisterForm

# Import your models here.
# from apps.operario.models import  Rep_Legal
from apps.tecnico.models import Operador_Nuevo, Docs_Legal, Vehiculo_Nuevo, Ruta
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
class Listar_Operadores(ListView):
    model = Operador_Nuevo
    template_name = 'operario/listar_operadores_nuevos.html'
    def get_queryset(self):
        querysets = super(Listar_Operadores, self).get_queryset()
        doc_legales = Docs_Legal.objects.filter(tipo='RESOLUCION_ADMINISTRATIVA')
        operador_in_doc_legales = []
        for doc_legal in doc_legales:
            operador_in_doc_legales.append(doc_legal.operador.id)
        queryset_operado_in_inf_tecnico = querysets.filter(vigente=True, es_nuevo=True, id__in=operador_in_doc_legales)
        return queryset_operado_in_inf_tecnico

class Registrar_Operador(UpdateView):
    model = Operador_Nuevo
    template_name = 'operario/registrar_operador.html'
    form_class = OpRegisterForm
    success_url = reverse_lazy('tecnico:operario_nuevo_listar')

    def form_valid(self, form):
        self.object = form.save(commit = False)
        print ('//////////' + str(self.kwargs['pk']))
        operador = Operador_Nuevo.objects.get(id=self.kwargs['pk'])
        self.object.es_nuevo = False
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('operario:operador_listar'))

class Listar_Detalle_Operadores(ListView):
    model = Operador_Nuevo
    template_name = 'operario/operador_list.html'
    def get_context_data(self, *args, **kwargs):
        context = super(Listar_Detalle_Operadores, self).get_context_data(*args, **kwargs)
        # Algoritmo para listar a los operadores nuevos
        doc_legales = Docs_Legal.objects.filter(tipo='RESOLUCION_ADMINISTRATIVA')
        operador_in_doc_legales = []
        for doc_legal in doc_legales:
            operador_in_doc_legales.append(doc_legal.operador.id)
        operado_tiene_resolucion_administrativa = Operador_Nuevo.objects.filter(vigente=True, es_nuevo=True, id__in=operador_in_doc_legales)
        context['operadores_nuevos'] = operado_tiene_resolucion_administrativa
        # print('ffffff---------------------'+ operado_tiene_resolucion_administrativa)

        operadores = Operador_Nuevo.objects.filter(es_nuevo=False)
        context['operador_n'] = operadores
        return context

class Actualizar_Operador(UpdateView):
    model = Operador_Nuevo
    template_name = 'operario/operador_actualizar.html'
    form_class = OperadorForm
    success_url = reverse_lazy('operario:operador_listar')

    # def form_valid(self, form):
    #     self.object = form.save(commit = False)
    #     print ('//////////' + str(self.kwargs['pk']))
    #     operador = Operador_Nuevo.objects.get(id=self.kwargs['pk'])
    #     self.object.save()
    #     return HttpResponseRedirect(reverse_lazy('operario:listar_operadores_nuevos'))

class Eliminar_Operador(DeleteView):
    model = Operador_Nuevo
    template_name = 'operario/operador_eliminar.html'
    success_url = reverse_lazy('operario:operador_listar')

class Detalle_Operadores(DetailView):
    model = Operador_Nuevo
    template_name = 'operario/detalle_operadores.html'
    def get_context_data(self, *args, **kwargs):
        context = super(Detalle_Operadores, self).get_context_data(*args, **kwargs)
        vehiculos_nuevos = Vehiculo_Nuevo.objects.filter(operador_id = self.kwargs['pk'], es_nuevo=True)
        vehiculo = Vehiculo_Nuevo.objects.filter(operador_id = self.kwargs['pk'], es_nuevo=False)
        rutas = Ruta.objects.filter(operador = self.kwargs['pk']).order_by('id')
        context['vehiculos_n'] = vehiculos_nuevos
        context['vehiculos'] = vehiculo
        context['formulario'] = RutaForm()
        context['rutas'] = rutas
        return context

class Registrar_Vehiculo(UpdateView):
    model = Vehiculo_Nuevo
    form_class = VehiRegisterForm
    template_name = 'operario/vehiculo_registrar.html'

    def form_valid(self, form):
        self.object = form.save(commit = False)
        operador = Operador_Nuevo.objects.get(id=self.kwargs['fk'])
        self.object.es_nuevo = False
        self.object.operador_id = operador.id
        self.object.tipo_id = 2
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('operario:operadores_detalle', kwargs = {
            'pk': operador.id
        }))
    
    def get_context_data(self, *args, **kwargs):
        context = super(Registrar_Vehiculo, self).get_context_data(*args, **kwargs)
        op = Operador_Nuevo.objects.get(id = self.kwargs['fk'])
        context['llave'] = op.id
        return context

class CrearRuta(CreateView):
    model = Ruta
    template_name = ''
    form_class = RutaForm
    def form_valid(self, form):
        self.object = form.save(commit = False)
        operador = Operador_Nuevo.objects.get(id=self.kwargs['pk'])
        self.object.operador = operador
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('operario:operadores_detalle', kwargs = {
            'pk': self.kwargs['pk']
        }))

class EliminarRuta(DeleteView):
    model = Ruta
    template_name = 'operario/ruta_eliminar.html'
    def get_success_url(self, **kwargs):
        return reverse_lazy('operario:operadores_detalle', kwargs = {
            'pk': self.kwargs['fk']})

    def get_context_data(self, *args, **kwargs):
        context = super(EliminarRuta, self).get_context_data(*args, **kwargs)
        #Mando la llave fk para el boton de cancelar
        context['llave'] = self.kwargs['fk'];
        return context

class Actualizar_Vehiculo(UpdateView):
    model = Vehiculo_Nuevo
    form_class = VehiculoForm
    template_name = 'operario/vehiculo_actualizar.html'

    def form_valid(self, form):
        self.object = form.save(commit = False)
        operador = Operador_Nuevo.objects.get(id=self.kwargs['fk'])
        self.object.es_nuevo = False
        self.object.operador_id = operador.id
        self.object.tipo_id = 1
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('operario:operadores_detalle', kwargs = {
            'pk': operador.id
        }))
    
    def get_context_data(self, *args, **kwargs):
        context = super(Actualizar_Vehiculo, self).get_context_data(*args, **kwargs)
        #Mando la llave fk para el boton de cancelar
        context['llave'] = self.kwargs['fk'];
        return context
    
class Eliminar_Vehiculo(DeleteView):
    model = Vehiculo_Nuevo
    template_name = 'operario/vehiculo_eliminar.html'
    def get_success_url(self, **kwargs):
        return reverse_lazy('operario:operadores_detalle', kwargs = {
            'pk': self.kwargs['fk']})

    def get_context_data(self, *args, **kwargs):
        context = super(Eliminar_Vehiculo, self).get_context_data(*args, **kwargs)
        #Mando la llave fk para el boton de cancelar
        context['llave'] = self.kwargs['fk'];
        return context

class ReportAnualOperador(View):
    def encabezado_pie(self, pdf, document):
        pdf.saveState()
        logo_gober = settings.MEDIA_ROOT+'/informes/logo7.png'
        logo_transporte = settings.MEDIA_ROOT+'/informes/logo_transporte.jpg'
        #Definimos el tamaño de la imagen a cargar y las coordenadas correspondientes
        pdf.drawImage(logo_gober, 100, 680, 60, 60,preserveAspectRatio=True)
        pdf.drawImage(logo_transporte, 450, 690, 80, 50)
        #Establecemos el tamaño de letra en 16 y el tipo de letra Helvetica
        pdf.setFont("Times-Roman", 12)
        #Dibujamos una cadena en la ubicación X,Y especificada
        pdf.drawString(190, 720, u"Gobierno Autónomo Departamental de Potosí")
        pdf.setFont("Times-Roman", 12)
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

    # def informe_devol(self, floables, spacer, styles, operador):
    #     styles.add(ParagraphStyle(name = "informe_devol",  alignment=TA_RIGHT, fontSize=10, fontName="Times-Roman"))
    #     informe = Informe.objects.get(operador=operador.id, tipo='DEVOLUCION')
    #     text = 'Potosí, {}'.format(informe.fecha)
    #     para = Paragraph(text, styles["informe_devol"] )
    #     floables.append(para)
    #     text = 'Cite ADM/URRT/DJD Nº {}/{}'.format(informe.cite, informe.fecha.year)
    #     para = Paragraph(text, styles["informe_devol"] )
    #     floables.append(para)
    
    # def dirigido(self, floables, spacer, styles, operador):
    #     styles.add(ParagraphStyle(name = "dirigido",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman"))
    #     floables.append(spacer)
    #     text = 'señor:'
    #     para = Paragraph(text, styles["dirigido"] )
    #     floables.append(para)
    #     nota = Nota.objects.get(operador_n=operador.id)
    #     text = '{}.'.format(nota.representante_ente)
    #     para = Paragraph(text, styles["dirigido"] )
    #     floables.append(para)
    #     text = '{} DEL(LA) {}.'.format(nota.cargo_repr.upper(), nota.nombre_ente.upper())
    #     para = Paragraph(text, styles["dirigido"] )
    #     floables.append(para)

    # def referencia(self, floables, spacer, styles, operador):
    #     styles.add(ParagraphStyle(name = "ref",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman"))
    #     floables.append(spacer)
    #     text = 'Presente.-'
    #     para = Paragraph(text, styles["ref"] )
    #     floables.append(para)
    #     text = 'Ref.: DEVOLUCION DE DOCUMENTACION DEL(LA) {}'.format(operador.nombre.upper())
    #     para = Paragraph(text, styles["ref"] )
    #     floables.append(para)

    # def inicio_carta(self, floables, spacer, styles, operador):
    #     styles.add(ParagraphStyle(name = "inicio",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman"))
    #     nota = Nota.objects.get(operador_n=operador.id)
    #     floables.append(spacer)
    #     text = 'De mi mayor consideración:'
    #     para = Paragraph(text, styles["inicio"] )
    #     floables.append(para)
    #     floables.append(spacer)
    #     text = '''La Unidad de Registro y Regulación de Transporte dependiente de la Dirección Jurídica del Gobierno Autónomo Departamental de Potosí, ha recibido lo siguiente: la nota del {} con Cite Nº {}/{} del {} afiliados a la {}, donde se solicita tramite de Tarjetas de Operación para un total de {} vehículos:
    #     '''.format(
    #         nota.fecha,
    #         nota.cite,
    #         nota.fecha.year,
    #         operador.nombre,
    #         nota.nombre_ente,
    #         nota.cantidad_tarjetas,
    #     )
    #     para = Paragraph(text, styles["inicio"] )
    #     floables.append(para)
    
    # def fin_carta(self, floables, spacer, styles, operador):
    #     styles.add(ParagraphStyle(name = "fin",  alignment=TA_JUSTIFY, fontSize=10, fontName="Times-Roman"))
    #     informe_obs = Informe.objects.get(operador=operador.id, tipo='OBSERVACION')
    #     floables.append(spacer)
    #     text = '''Es en este sentido que en fecha {} con Cite ADM/URRT/DJD N° {}/{} se efectuó la observación al {} quienes no subsanaron estas observaciones Hasta la fecha..'''.format(
    #         informe_obs.fecha,
    #         informe_obs.cite,
    #         informe_obs.fecha.year,
    #         operador.nombre,
    #         )
    #     para = Paragraph(text, styles["fin"] )
    #     floables.append(para)
    #     text = '''Teniendo estos antecedentes, se efectúa la devolución de la documentación de la documentación presentada por que no cumple con los requisitos del Reglamento de Transporte Interprovincial e Intermunicipal de Carga y/o Pasajeros del Departamento de Potosí'''
    #     para = Paragraph(text, styles["fin"] )
    #     floables.append(para)
    #     floables.append(spacer)
    #     text = '''Sin otro particulaer motivo, me despido con las consideraciones más distinguidas'''
    #     para = Paragraph(text, styles["fin"] )
    #     floables.append(para)

    def reporte(self, floables, spacer, styles, operadores):
        styles.add(ParagraphStyle(name = "reporte",  alignment=TA_CENTER, fontSize=10, fontName="Times-Roman"))
        styles.add(ParagraphStyle(name = "tittle",  alignment=TA_CENTER, fontSize=12, fontName="Times-Bold"))
        # floables.append(spacer)
        text = '''REPORTE DE OPERADORES'''
        para = Paragraph(text, styles["tittle"] )
        floables.append(para)
        floables.append(spacer)
                
        encabezado_tabla=['No.', 'Nombre', 'Tipo', 'Modalidad','Nit', 'Razon Social']
        data = [encabezado_tabla]
        num = 1
        for operador in operadores:
            fila = []
            fila.append(Paragraph(str(num), styles["reporte"]))
            fila.append(Paragraph(operador.nombre.upper(), styles["reporte"]))
            fila.append(Paragraph(operador.tipo.upper(), styles["reporte"]))
            fila.append(Paragraph(operador.modalidad.upper(), styles["reporte"]))
            fila.append(Paragraph(operador.nit, styles["reporte"]))
            fila.append(Paragraph(operador.razon_social.nombre.upper(), styles["reporte"]))
            data.append(fila)
            num += 1
        print('++++++++****'+ str(data))

        tabla = Table(data = data, style = [('GRID',(0,0),(-1,-1),0.5,colors.grey),])
        # tabla = Table(data = data, style = [('GRID',(0,0),(-1,-1),0.5,colors.grey),], colWidths=[22,150,60,210] )
        floables.append(tabla)

    def get(self, request, *args, **kwargs):
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
        # Obtener a los operadores
        operadores = Operador_Nuevo.objects.filter(es_nuevo=False)
        self.reporte(flowables, spacer, styles, operadores)
        doc.build(flowables, onFirstPage=self.encabezado_pie, onLaterPages=self.encabezado_pie)
        response.write(buffer.getvalue())
        buffer.close()
        return response









# class dar_Baja_Vehiculo(UpdateView):
#     model = Vehiculo_Nuevo
#     form_class = VehiculoForm
#     template_name = 'operario/daja_vehiculo.html'

#     def form_valid(self, form):
#         vehiculo = Vehiculo_Nuevo.objects.get(id=self.object.id)
#         vehiculo.dar_baja = True
#         vehiculo.save()
#         return HttpResponseRedirect(reverse_lazy('operario:operadores_detalle', kwargs = {
#             'pk': operador.id
#         }))
    
#     def get_context_data(self, *args, **kwargs):
#         context = super(Actualizar_Vehiculo, self).get_context_data(*args, **kwargs)
#         #Mando la llave fk para el boton de cancelar
#         context['llave'] = self.kwargs['fk'];
#         return context
















#Aun no se si es necesario crear un representante para el operario
# class RepresentanteCreate(CreateView):
#     model = Rep_Legal
#     template_name = 'operario/operario_form.html'
#     form_class = RepresentanteForm
#     second_form_class = OperarioForm
#     success_url = reverse_lazy('operario:operario_crear')
    
#     def get_context_data(self, **kwargs):
#         context = super(RepresentanteCreate, self).get_context_data(**kwargs)
#         if 'form' not in context:
#             context['form'] = self.form_class(self.request.GET)
#         if 'form2' not in context:
#             context['form2'] = self.second_form_class(self.request.GET)
#         context['media'] = settings.MEDIA_ROOT
#         return context
    
#     def post(self, request, *args, **kwargs):
#         self.object = self.get_object
#         form = self.form_class(request.POST)
#         form2 = self.second_form_class(request.POST, request.FILES)
#         if form.is_valid() and form2.is_valid():
#             representante = form.save(commit=False)
#             representante.operario = form2.save()
#             representante.save()
#             return HttpResponseRedirect(self.get_success_url())
#         else:
#             return self.render_to_response(self.get_context_data(form=form, form2=form2))

# class RepresentanteUpdate(UpdateView):
#     model = Rep_Legal
#     second_model = Operario
#     template_name = 'operario/operario_form.html'
#     form_class = RepresentanteForm
#     second_form_class = OperarioForm
#     success_url = reverse_lazy('operario:operario_crear')

#     def get_context_data(self, **kwargs):
#         context = super(RepresentanteUpdate, self).get_context_data(**kwargs)
#         pk = self.kwargs.get('pk',0)
#         representante = self.model.objects.get(id=pk)
#         operario = self.second_model.objects.get(id=representante.operario_id)
#         if 'form' not in context:
#             context['form'] = self.form_class()
#         if 'form2' not in context:
#             context['form2'] = self.second_form_class(instance=operario)
#         context['id'] = pk
#         return context
    
#     def post(self, request, *args, **kwargs):
#         self.object = self.get_object
#         id_responsable = kwargs['pk']
#         representante = self.model.objects.get(id=id_responsable)
#         operario = self.second_model.objects.get(id=representante.operario_id)
#         form = self.form_class(request.POST)
#         form2 = self.second_form_class(request.POST, instance=operario)
#         if form.is_valid() and form2.is_valid():
#             form.save()
#             form2.save()
#             return HttpResponseRedirect(self.get_success_url())
#         else:
#             return HttpResponseRedirect(self.get_success_url())
            