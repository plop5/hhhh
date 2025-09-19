from django import forms
from .models import Acompanante
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.utils.translation import gettext_lazy as _

class UserCreationForm(DjangoUserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['username'].help_text = 'Obligatorio. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ únicamente.'
        self.fields['email'].label = 'Correo electrónico'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password1'].help_text = 'Requisitos de la contraseña:'
        self.fields['password2'].label = 'Confirmar contraseña'
        self.fields['password2'].help_text = 'Introduce la misma contraseña que antes, para verificación.'

    class Meta:
        model = Acompanante
        fields = ('username', 'email', 'password1', 'password2')
