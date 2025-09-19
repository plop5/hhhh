# rankings/admin.py

from django.contrib import admin
from .models import Calificacion, PerfilExtendido, AnuncioExtendido

@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ['anuncio', 'puntuacion', 'nombre_cliente', 'fecha', 'verificado']
    list_filter = ['verificado', 'puntuacion', 'fecha']
    search_fields = ['anuncio__titulo', 'nombre_cliente', 'email_cliente']
    actions = ['marcar_como_verificado', 'marcar_como_no_verificado']
    
    def marcar_como_verificado(self, request, queryset):
        queryset.update(verificado=True)
        for calificacion in queryset:
            calificacion.actualizar_puntuacion_anuncio()
    marcar_como_verificado.short_description = "Marcar como verificado"
    
    def marcar_como_no_verificado(self, request, queryset):
        queryset.update(verificado=False)
        for calificacion in queryset:
            calificacion.actualizar_puntuacion_anuncio()
    marcar_como_no_verificado.short_description = "Marcar como no verificado"

@admin.register(PerfilExtendido)
class PerfilExtendidoAdmin(admin.ModelAdmin):
    list_display = ['acompanante', 'email_verificado', 'telefono_verificado', 'puntuacion_ranking']
    list_filter = ['email_verificado', 'telefono_verificado', 'documento_verificado']
    search_fields = ['acompanante__username', 'acompanante__email']

@admin.register(AnuncioExtendido)
class AnuncioExtendidoAdmin(admin.ModelAdmin):
    list_display = ['anuncio', 'categoria', 'activo', 'destacado', 'puntuacion_promedio']
    list_filter = ['categoria', 'activo', 'destacado', 'vip']
    search_fields = ['anuncio__titulo', 'anuncio__usuario__username']
