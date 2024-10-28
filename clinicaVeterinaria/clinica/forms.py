from django import forms
from django.utils import timezone
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
    
class RegistroVetForm(UserCreationForm):
    class Meta:
        model = Veterinario
        fields = ['dni', 'especialidad']

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
    
    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')

        if fecha.date() < timezone.now().date():
            raise forms.ValidationError("La fecha de la cita no puede ser anterior a la fecha actual.")
        
        return fecha

class EditCitaForm(forms.ModelForm):

    class Meta:
        model = Citas
        fields = ['fecha', 'hora']
    
    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')

        if fecha.date() < timezone.now().date():
            raise forms.ValidationError("La fecha de la cita no puede ser anterior a la fecha actual.")
        
        return fecha
    
class PasswordChangeForm(DjangoPasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        
        self.fields['old_password'].error_messages = {
            'required': 'Por favor, introduce tu contraseña actual.',
            'invalid': 'La contraseña actual que has ingresado es incorrecta.'
        }
        
        self.fields['new_password1'].error_messages = {
            'required': 'Debes introducir una nueva contraseña.',
            'password_mismatch': 'Las contraseñas no coinciden.',
            'password_too_common': 'Esta contraseña es demasiado común. Elige otra.'
        }

        self.fields['new_password2'].error_messages = {
            'required': 'Debes confirmar tu nueva contraseña.',
            'password_mismatch': 'Las contraseñas no coinciden.'
        }

class HistorialMedicoForm(forms.ModelForm):
    class Meta:
        model = HistorialMedico
        fields = ['medicacion', 'descripcion']

        widgets = {
            'medicacion': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ingrese la medicación'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Descripción del historial',
                'rows': 4
            }),
        }
    
    
