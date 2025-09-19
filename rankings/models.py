# rankings/models.py
"""
Modelos para el sistema de rankings y calificaciones
Separado de la app accounts para evitar problemas de migración
"""

from django.db import models
from django.db.models import Avg
from accounts.models import Anuncio, Acompanante

class Calificacion(models.Model):
    """Modelo para calificaciones de clientes a escorts"""
    anuncio = models.ForeignKey(Anuncio, on_delete=models.CASCADE, related_name='calificaciones')
    nombre_cliente = models.CharField(max_length=100)  # Nombre opcional del cliente
    email_cliente = models.EmailField()  # Para verificar una sola calificación por cliente
    puntuacion = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 estrellas
    comentario = models.TextField(blank=True)
    
    # Categorías específicas de calificación
    trato = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    puntualidad = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    higiene = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    servicio = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    
    # Metadatos
    fecha = models.DateTimeField(auto_now_add=True)
    ip_cliente = models.GenericIPAddressField(null=True, blank=True)
    verificado = models.BooleanField(default=False)  # Admin verifica autenticidad
    
    class Meta:
        unique_together = ['anuncio', 'email_cliente']  # Una calificación por email por anuncio
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Actualizar puntuación del anuncio cuando se guarda una calificación
        self.actualizar_puntuacion_anuncio()
    
    def actualizar_puntuacion_anuncio(self):
        """Actualiza la puntuación promedio del anuncio"""
        calificaciones_verificadas = Calificacion.objects.filter(
            anuncio=self.anuncio, 
            verificado=True
        )
        
        if calificaciones_verificadas.exists():
            promedio = calificaciones_verificadas.aggregate(Avg('puntuacion'))['puntuacion__avg']
            # Actualizamos campos en el anuncio (los agregamos después)
            self.anuncio.puntuacion_promedio = round(promedio, 1)
            self.anuncio.total_calificaciones = calificaciones_verificadas.count()
        else:
            self.anuncio.puntuacion_promedio = 0.0
            self.anuncio.total_calificaciones = 0
        
        self.anuncio.save()

    def __str__(self):
        return f"Calificación {self.puntuacion}★ para {self.anuncio.titulo}"

class PerfilExtendido(models.Model):
    """Campos adicionales para el perfil del acompañante"""
    acompanante = models.OneToOneField(Acompanante, on_delete=models.CASCADE, related_name='perfil_extendido')
    
    # Verificaciones
    telefono_verificado = models.BooleanField(default=False)
    email_verificado = models.BooleanField(default=False)
    documento_verificado = models.BooleanField(default=False)
    
    # Ranking
    puntuacion_ranking = models.FloatField(default=0.0)
    posicion_ranking = models.IntegerField(default=0)
    
    # Campos adicionales del formulario
    etnia = models.CharField(max_length=50, blank=True)
    nacionalidad = models.CharField(max_length=50, blank=True)
    sobre_ti = models.TextField(blank=True)
    
    # Estadísticas
    total_visitas = models.IntegerField(default=0)
    total_contactos = models.IntegerField(default=0)
    
    def calcular_ranking(self):
        """Calcula el puntaje de ranking basado en varios factores"""
        score = 0
        
        # 1. Promedio de calificaciones (40% del score)
        calificaciones = Calificacion.objects.filter(
            anuncio__usuario=self.acompanante, 
            verificado=True
        )
        if calificaciones.exists():
            promedio = calificaciones.aggregate(Avg('puntuacion'))['puntuacion__avg']
            score += (promedio / 5.0) * 40
        
        # 2. Completitud del perfil (20% del score)
        completitud = self.calcular_completitud_perfil()
        score += completitud * 20
        
        # 3. Número de anuncios activos (15% del score)
        anuncios_activos = self.acompanante.anuncios.filter(activo=True).count()
        score += min(15, anuncios_activos * 5)
        
        # 4. Verificaciones (15% del score)
        verificaciones = 0
        if self.email_verificado: verificaciones += 1
        if self.telefono_verificado: verificaciones += 1
        if self.documento_verificado: verificaciones += 1
        score += (verificaciones / 3.0) * 15
        
        # 5. Actividad reciente (10% del score)
        from django.utils import timezone
        if self.acompanante.anuncios.exists():
            ultimo_anuncio = self.acompanante.anuncios.latest('actualizado')
            dias_inactivo = (timezone.now() - ultimo_anuncio.actualizado).days
            score += max(0, 10 - dias_inactivo)
        
        self.puntuacion_ranking = round(score, 2)
        self.save()
        return self.puntuacion_ranking
    
    def calcular_completitud_perfil(self):
        """Calcula qué tan completo está el perfil (0-1)"""
        campos_requeridos = [
            self.acompanante.first_name, 
            self.acompanante.email, 
            self.acompanante.ciudad, 
            self.acompanante.genero,
            self.etnia, 
            self.nacionalidad, 
            self.sobre_ti
        ]
        campos_completos = sum(1 for campo in campos_requeridos if campo)
        return campos_completos / len(campos_requeridos)

    def __str__(self):
        return f"Perfil extendido de {self.acompanante.username}"

class AnuncioExtendido(models.Model):
    """Campos adicionales para los anuncios"""
    anuncio = models.OneToOneField(Anuncio, on_delete=models.CASCADE, related_name='anuncio_extendido')
    
    # Nuevos campos del formulario
    categoria = models.CharField(max_length=50, choices=[
        ('escorts-femeninos', 'Escort Femenino'),
        ('escorts-masculinos', 'Escort Masculino'),
        ('trans-travestis', 'Trans y Travestis'),
    ], default='escorts-femeninos')
    direccion = models.CharField(max_length=200, blank=True)
    barrio = models.CharField(max_length=100, blank=True)
    edad = models.IntegerField(default=18)
    detalle_sexo = models.CharField(max_length=100, blank=True)
    
    # Servicios
    servicios = models.TextField(blank=True)
    atiende_a = models.CharField(max_length=100, blank=True)
    lugar = models.CharField(max_length=100, blank=True)
    pago_efectivo = models.BooleanField(default=False)
    pago_tarjeta = models.BooleanField(default=False)
    
    # Contacto
    telefono = models.CharField(max_length=15, blank=True)
    whatsapp = models.BooleanField(default=False)
    correo = models.EmailField(blank=True)
    mostrar_contacto = models.CharField(max_length=20, choices=[
        ('ambos', 'Teléfono y correo'),
        ('telefono', 'Solo teléfono'),
        ('correo', 'Solo correo'),
    ], default='ambos')
    
    # Estado y ranking
    activo = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)
    vip = models.BooleanField(default=False)
    puntuacion_promedio = models.FloatField(default=0.0)
    total_calificaciones = models.IntegerField(default=0)
    
    # Estadísticas
    visualizaciones = models.IntegerField(default=0)
    clicks_contacto = models.IntegerField(default=0)
    
    def get_primera_foto(self):
        """Obtiene la primera foto del anuncio para mostrar en rankings"""
        primera_foto = self.anuncio.fotos.first()
        return primera_foto.imagen.url if primera_foto else '/static/img/no-image.jpg'
    
    def get_servicios_lista(self):
        """Convierte servicios en lista para mostrar"""
        return [s.strip() for s in self.servicios.split(',') if s.strip()] if self.servicios else []

    def __str__(self):
        return f"Datos extendidos de {self.anuncio.titulo}"
