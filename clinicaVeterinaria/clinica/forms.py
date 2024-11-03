from django import forms
from django.utils import timezone
from datetime import datetime
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm

class PasswordChangeForm(DjangoPasswordChangeForm):
    pass

from .models import *

RAZAS_VALIDAS = [
    "Labrador", "Retriever", "Golden Retriever", "Bulldog", "Beagle", "Poodle", 
    "Chihuahua", "Shih Tzu", "Yorkshire Terrier", "Dachshund", "Boxer"
]

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
    
class RegistroVetForm(forms.ModelForm):
    class Meta:
        model = Veterinario
        fields = ['especialidad']

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if Veterinario.objects.filter(dni=dni).exists():
            raise forms.ValidationError("Ya existe un veterinario con ese DNI.")
        return dni

    def save(self, commit=True):
        user = super(RegistroVetForm, self).save(commit=False)

        user.hora_entrada = time(7, 0)  
        user.hora_salida = time(15, 0)
        
        if commit:
            user.save()
        return user

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Usuario  
        fields = ['first_name', 'email', 'telefono', 'direccion', 'foto']
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists() and self.instance.email != email:
            raise forms.ValidationError("El correo electrónico ya está en uso.")
        return email
    
class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ['nombre', 'edad', 'raza', 'descripcion', 'foto']

    def clean_raza(self):
        raza = self.cleaned_data.get('raza')
        if raza not in RAZAS_VALIDAS:
            raise forms.ValidationError(f"La raza {raza} no es válida. Elige una raza de la lista permitida.")
        return raza
    
class GenerarCodigoForm(forms.Form):
    cantidad = forms.IntegerField(min_value=1, required=True)

class CitaForm(forms.ModelForm):
    urgente = forms.BooleanField(required=False, label='Urgente')

    class Meta:
        model = Citas
        fields = ['nombre', 'idM', 'fecha', 'hora', 'motivo']
    
    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')
        mascota = cleaned_data.get('idM')

        if fecha and hora:
            fecha_hora_cita = timezone.make_aware(datetime.combine(fecha, hora))
            if fecha_hora_cita <= timezone.now():
                raise forms.ValidationError("La fecha y hora de la cita deben ser futuras.", code="Fecha")


        if mascota and fecha and hora:
            if Citas.objects.filter(idM=mascota, fecha=fecha, hora=hora).exists():
                raise forms.ValidationError("La mascota ya tiene una cita en esta fecha y hora.")

        veterinarios_ocupados = Citas.objects.filter(fecha=fecha, hora=hora).values_list('dni', flat=True)
        veterinarios_disponibles = Veterinario.objects.exclude(dni__in=veterinarios_ocupados)

        if not veterinarios_disponibles:
            raise forms.ValidationError("No hay veterinarios disponibles para esta fecha y hora.")

        return cleaned_data

class EditCitaForm(forms.ModelForm):

    class Meta:
        model = Citas
        fields = ['fecha', 'hora']
    
    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')

        if fecha and hora:
            fecha_hora_cita = timezone.make_aware(datetime.combine(fecha, hora))
            if fecha_hora_cita <= timezone.now():
                raise forms.ValidationError("La fecha y hora de la cita deben ser futuras.")


        if fecha and hora:
            if Citas.objects.filter(fecha=fecha, hora=hora).exists():
                raise forms.ValidationError("La mascota ya tiene una cita en esta fecha y hora.")

        veterinarios_ocupados = Citas.objects.filter(fecha=fecha, hora=hora).values_list('dni', flat=True)
        veterinarios_disponibles = Veterinario.objects.exclude(dni__in=veterinarios_ocupados)

        if not veterinarios_disponibles:
            raise forms.ValidationError("No hay veterinarios disponibles para esta fecha y hora.")

        return cleaned_data
    
class PasswordChangeForm(DjangoPasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")
        if not self.user.check_password(old_password):
            raise forms.ValidationError('Tu contraseña actual es incorrecta.')
        return old_password

    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get("new_password1")
        # Agrega aquí más validaciones si es necesario
        if len(new_password1) < 8:
            raise forms.ValidationError('La nueva contraseña es demasiado corta. Debe tener al menos 8 caracteres.')
        return new_password1

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get("new_password1")
        new_password2 = self.cleaned_data.get("new_password2")
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError('Las contraseñas no coinciden.')
        return new_password2