from django.contrib import admin
from .models import Acompanante, Anuncio, FotoAnuncio

@admin.register(Acompanante)
class AcompananteAdmin(admin.ModelAdmin):
	list_display = ("username", "email", "plan", "ciudad", "genero")
	list_filter = ("plan", "ciudad", "genero")
	search_fields = ("username", "email")

@admin.register(Anuncio)
class AnuncioAdmin(admin.ModelAdmin):
	list_display = ("titulo", "usuario", "ciudad", "precio", "sexo", "creado")
	list_filter = ("ciudad", "sexo")
	search_fields = ("titulo", "descripcion")

@admin.register(FotoAnuncio)
class FotoAnuncioAdmin(admin.ModelAdmin):
	list_display = ("anuncio", "subida")
