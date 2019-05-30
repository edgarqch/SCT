"""sit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
# from django.urls import path
from django.contrib.auth.views import login, logout_then_login

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^tramite/', include('apps.tramite.urls', namespace="tramite")),
    url(r'^vehiculo/', include('apps.vehiculo.urls', namespace="vehiculo")),
    url(r'^operador/', include('apps.operario.urls', namespace="operario")),
    url(r'^tecnico/', include('apps.tecnico.urls', namespace="tecnico")),
    url(r'^usuario/', include('apps.usuario.urls', namespace="usuario")),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    # url(r'^accounts/login/', login,{'template_name':'index.html'}, name='login'),
    url(r'^', login,{'template_name':'index.html'}, name='login'),
    url(r'^logout/', logout_then_login, name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_URL)
