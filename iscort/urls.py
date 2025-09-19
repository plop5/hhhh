"""
URL configuration for iscort project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from accounts import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('panel/', views.panel, name='panel'),
    path('acompanantes/', views.listado_acompanantes, name='listado_acompanantes'),
    path('mis-anuncios/', views.mis_anuncios, name='mis_anuncios'),
    path('publicaciones/', views.listado_publico, name='listado_publico'),
    path('publicaciones/<str:categoria>/', views.listado_publico, name='listado_publico_categoria'),
    path('publicaciones/<str:categoria>/<str:ciudad>/', views.listado_publico, name='listado_publico_categoria_ciudad'),
    path('publicar/', views.unisex_form, name='unisex_form'),
    path('fotos-user/', views.fotos_user, name='fotos_user'),
    path('logout/', views.logout_view, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
