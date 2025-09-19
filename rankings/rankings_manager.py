# rankings/rankings_manager.py
"""
Sistema de Rankings para iScort
Maneja toda la lógica de rankings y top lists
"""

from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta
from accounts.models import Anuncio, Acompanante
from .models import Calificacion, AnuncioExtendido

class RankingManager:
    """Clase para manejar todos los rankings de la plataforma"""
    
    @staticmethod
    def get_top_escorts_femeninos(limit=10):
        """Obtiene el top de escorts femeninos"""
        return Anuncio.objects.filter(
            sexo__in=['mujer', 'femenino'],
            # Cuando migremos: anuncio_extendido__categoria='escorts-femeninos',
            # anuncio_extendido__activo=True
        ).annotate(
            avg_rating=Avg('calificaciones__puntuacion', filter=Q(calificaciones__verificado=True)),
            total_reviews=Count('calificaciones', filter=Q(calificaciones__verificado=True))
        ).order_by('-avg_rating', '-total_reviews', '-actualizado')[:limit]
    
    @staticmethod
    def get_top_escorts_masculinos(limit=10):
        """Obtiene el top de escorts masculinos"""
        return Anuncio.objects.filter(
            sexo__in=['hombre', 'masculino'],
        ).annotate(
            avg_rating=Avg('calificaciones__puntuacion', filter=Q(calificaciones__verificado=True)),
            total_reviews=Count('calificaciones', filter=Q(calificaciones__verificado=True))
        ).order_by('-avg_rating', '-total_reviews', '-actualizado')[:limit]
    
    @staticmethod
    def get_top_trans_travestis(limit=10):
        """Obtiene el top de trans y travestis"""
        return Anuncio.objects.filter(
            sexo__in=['trans', 'travesti'],
        ).annotate(
            avg_rating=Avg('calificaciones__puntuacion', filter=Q(calificaciones__verificado=True)),
            total_reviews=Count('calificaciones', filter=Q(calificaciones__verificado=True))
        ).order_by('-avg_rating', '-total_reviews', '-actualizado')[:limit]
    
    @staticmethod
    def get_top_por_ciudad(ciudad, limit=10):
        """Obtiene el top de escorts por ciudad específica"""
        return Anuncio.objects.filter(
            ciudad__iexact=ciudad,
        ).annotate(
            avg_rating=Avg('calificaciones__puntuacion', filter=Q(calificaciones__verificado=True)),
            total_reviews=Count('calificaciones', filter=Q(calificaciones__verificado=True))
        ).order_by('-avg_rating', '-total_reviews', '-actualizado')[:limit]
    
    @staticmethod
    def get_destacados_del_mes(limit=6):
        """Obtiene los escorts destacados del mes"""
        hace_un_mes = timezone.now() - timedelta(days=30)
        
        return Anuncio.objects.filter(
            calificaciones__fecha__gte=hace_un_mes,
            calificaciones__verificado=True
        ).annotate(
            avg_rating=Avg('calificaciones__puntuacion'),
            total_reviews=Count('calificaciones'),
            reviews_recientes=Count('calificaciones', filter=Q(calificaciones__fecha__gte=hace_un_mes))
        ).filter(
            avg_rating__gte=4.0,  # Mínimo 4 estrellas
            total_reviews__gte=3   # Mínimo 3 reviews
        ).order_by('-avg_rating', '-reviews_recientes')[:limit]
    
    @staticmethod
    def get_nuevos_verificados(limit=8):
        """Obtiene escorts nuevos y verificados"""
        hace_dos_semanas = timezone.now() - timedelta(days=14)
        
        return Anuncio.objects.filter(
            creado__gte=hace_dos_semanas,
            # Cuando migremos: usuario__perfil_extendido__email_verificado=True
        ).order_by('-creado')[:limit]
    
    @staticmethod
    def get_mejores_por_trato(limit=10):
        """Obtiene los mejores por trato al cliente"""
        return Anuncio.objects.filter(
            calificaciones__verificado=True
        ).annotate(
            avg_trato=Avg('calificaciones__trato'),
            total_reviews=Count('calificaciones')
        ).filter(
            avg_trato__isnull=False,
            total_reviews__gte=2
        ).order_by('-avg_trato', '-total_reviews')[:limit]
    
    @staticmethod
    def get_estadisticas_generales():
        """Obtiene estadísticas generales para mostrar en home"""
        total_escorts = Anuncio.objects.count()
        total_ciudades = Anuncio.objects.values('ciudad').distinct().count()
        total_reviews = Calificacion.objects.filter(verificado=True).count()
        
        # Promedio general de satisfacción
        promedio_general = Calificacion.objects.filter(
            verificado=True
        ).aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0
        
        return {
            'total_escorts': total_escorts,
            'total_ciudades': total_ciudades,
            'total_reviews': total_reviews,
            'promedio_satisfaccion': round(promedio_general, 1) if promedio_general else 0
        }

class RankingDisplay:
    """Clase para formatear datos de rankings para mostrar en templates"""
    
    @staticmethod
    def format_anuncio_for_ranking(anuncio):
        """Formatea un anuncio para mostrar en rankings"""
        # Obtener primera foto
        primera_foto = anuncio.fotos.first()
        foto_url = primera_foto.imagen.url if primera_foto else '/static/img/no-image.jpg'
        
        # Calcular promedio de calificaciones
        calificaciones = anuncio.calificaciones.filter(verificado=True)
        promedio = 0
        total_reviews = 0
        if calificaciones.exists():
            promedio = round(calificaciones.aggregate(Avg('puntuacion'))['puntuacion__avg'], 1)
            total_reviews = calificaciones.count()
        
        return {
            'id': anuncio.id,
            'titulo': anuncio.titulo,
            'usuario': anuncio.usuario.first_name or anuncio.usuario.username,
            'ciudad': anuncio.ciudad,
            'precio': anuncio.precio,
            'puntuacion': promedio,
            'total_reviews': total_reviews,
            'foto_principal': foto_url,
            'categoria': anuncio.sexo,
            'telefono': None,  # Por ahora no mostramos teléfono
            'servicios': [],   # Por ahora vacío
            'created': anuncio.creado,
        }
    
    @staticmethod
    def get_home_rankings():
        """Obtiene todos los rankings para mostrar en la página principal"""
        return {
            'top_femeninos': [
                RankingDisplay.format_anuncio_for_ranking(anuncio) 
                for anuncio in RankingManager.get_top_escorts_femeninos(6)
            ],
            'top_masculinos': [
                RankingDisplay.format_anuncio_for_ranking(anuncio) 
                for anuncio in RankingManager.get_top_escorts_masculinos(6)
            ],
            'top_trans': [
                RankingDisplay.format_anuncio_for_ranking(anuncio) 
                for anuncio in RankingManager.get_top_trans_travestis(6)
            ],
            'destacados_mes': [
                RankingDisplay.format_anuncio_for_ranking(anuncio) 
                for anuncio in RankingManager.get_destacados_del_mes(6)
            ],
            'nuevos_verificados': [
                RankingDisplay.format_anuncio_for_ranking(anuncio) 
                for anuncio in RankingManager.get_nuevos_verificados(6)
            ],
            'estadisticas': RankingManager.get_estadisticas_generales()
        }
