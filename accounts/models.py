from django.db import models
from django.contrib.auth.models import AbstractUser

class Acompanante(AbstractUser):
    # Datos básicos originales
    ciudad = models.CharField(max_length=100)
    genero = models.CharField(max_length=20)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    PLAN_CHOICES = [
        ('basico', 'Básico'),
        ('premium', 'Premium'),
        ('vip', 'VIP'),
    ]
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default='basico')

    def __str__(self):
        return self.username

class Anuncio(models.Model):
    # Campos originales únicamente
    usuario = models.ForeignKey(Acompanante, on_delete=models.CASCADE, related_name='anuncios')
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    ciudad = models.CharField(max_length=100)
    pais = models.CharField(max_length=50, default='Ecuador')
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    sexo = models.CharField(max_length=20)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"

class FotoAnuncio(models.Model):
    anuncio = models.ForeignKey(Anuncio, on_delete=models.CASCADE, related_name='fotos')
    imagen = models.ImageField(upload_to='anuncios_fotos/')
    subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foto de {self.anuncio.titulo} ({self.id})"
