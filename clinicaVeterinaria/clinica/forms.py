from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *

class RegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'dni', 'telefono', 'direccion', 'ciudad', 'pais', 'codigo_postal', 'password1', 'password2']
    
    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        
        if Usuario.objects.filter(dni=dni).exists():
            raise forms.ValidationError("Ya existe un usuario con ese DNI.")
        return dni

    def save(self, commit=True):
        user = super(RegistroForm, self).save(commit=False)

        if commit:
            user.save()
        return user