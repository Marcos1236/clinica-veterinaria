from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.views.generic import TemplateView
from django.http import JsonResponse
from .forms import *
from .models import *
from .decorators import es_cliente, es_veterinario
from django.http import HttpResponse, HttpResponseForbidden
from datetime import datetime, timedelta
import random
import string
import json
import traceback


def index(request):
    if request.user.is_authenticated:
        return redirect('calendar')
    return render(request, "clinica/pantallaCarga.html")

@staff_member_required
def generateCode(request):
    if request.method == 'POST':
        form = GenerarCodigoForm(request.POST)
        if form.is_valid():
            cantidad = form.cleaned_data['cantidad']
            for _ in range(cantidad):
                # Genera un código único
                codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                CodigoRegistro.objects.create(codigo=codigo)
            messages.success(request, f'Se han generado {cantidad} códigos nuevos.')
            return redirect('generateCode')
    else:
        form = GenerarCodigoForm()
    
    codigos = CodigoRegistro.objects.all()
    return render(request, 'clinica/generateCode.html', {'form': form, 'codigos': codigos})

def registerClient(request):
    if request.user.is_authenticated:
        return redirect('calendar')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()  

            Cliente.objects.create(dni=usuario)

            messages.success(request, '¡Tu cuenta ha sido creada con éxito!')
            return redirect('login')  

    else:
        form = RegistroForm()
    
    return render(request, 'clinica/registroCliente.html', {'form': form})

def registerVet(request):
    if request.user.is_authenticated:
        return redirect('calendar')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        codigo_ingresado = request.POST.get('codigo_registro')

        try:
            codigo = CodigoRegistro.objects.get(codigo=codigo_ingresado, utilizado=False)
        except CodigoRegistro.DoesNotExist:
            print('Código de registro inválido o ya utilizado.')
            return render(request, 'clinica/registroVeterinario.html', {'form': form})

        if form.is_valid():
            usuario = form.save()
            hora_entrada = "07:00:00"
            hora_salida = "15:00:00"
            Veterinario.objects.create(dni=usuario, hora_entrada=hora_entrada, hora_salida=hora_salida)

            codigo.utilizado = True
            codigo.save()

            messages.success(request, '¡Tu cuenta ha sido creada con éxito!')
            return redirect('login')
        else:
            print("Form no válido. Errores:", form.errors)

    else:
        form = RegistroForm()

    return render(request, 'clinica/registroVeterinario.html', {'form': form})

def login(request):
    if request.user.is_authenticated:
        return redirect('calendar')
     
    if request.method == 'POST':
        username = request.POST.get('username')  
        password = request.POST.get('password')
        
        usuario = authenticate(request, username=username, password=password)  
        if usuario is not None:
            auth_login(request, usuario)  
            return redirect('calendar') 
        else:
            print("Adios")
            messages.error(request, 'Credenciales incorrectas.')
    
    return render(request, 'clinica/login.html')

def logout(request):
    auth_logout(request)
    return redirect('login')

@login_required
def calendar(request):
    user = Usuario.objects.get(dni=request.user.dni)

    if Cliente.objects.filter(dni=request.user).exists():
        mascotas = Mascota.objects.filter(dni=user.dni)
        citas = Citas.objects.filter(idM__in=mascotas)
        vets = Veterinario.objects.all()

        if request.method == 'POST':
            mascota = request.POST.get('mascota')

            if 'clear_filter' in request.POST:
                citas = Citas.objects.filter(idM__in=mascotas) 
            elif mascota:
                citas = Citas.objects.filter(idM_id=mascota)

        form = CitaForm()
        events = generate_events(citas)

        context = {
            'events': json.dumps(events),
            'form': form,
            'mascotas': mascotas,
            'vets': vets,
            'user' : request.user,
        }
        return render(request, 'clinica/calendario_cliente.html', context)

    elif Veterinario.objects.filter(dni=request.user).exists():
        citas = Citas.objects.filter(dni=user.dni)
        context = {
            'events': citas,
            'user': request.user
        }
        return render(request, 'clinica/calendario_veterinario.html', context)

@login_required
def addEvent(request):
    if request.method == 'POST':

        form = CitaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.tipo = 'U' if 'tipo' in request.POST else 'R'
            cita.save()
            messages.success(request, 'La cita ha sido creada correctamente.')
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, f"Error en {field.label}: {error}")
        return redirect('calendar') 

@login_required
def editEvent(request):
    if request.method == 'POST':
        
        try:
            cita = Citas.objects.get(id=request.POST.get('cita_id'))  # Cambia 'Cita' por el nombre real de tu modelo
        except Citas.DoesNotExist:
            messages.error(request, 'La cita no existe.')
            return redirect('calendar')
        
        form = EditCitaForm(request.POST, request.FILES, instance=cita)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.save()
            messages.info(request, 'La cita ha sido modificada.')
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, f"Error en {field.label}: {error}")
        return redirect('calendar') 
@login_required
def deleteEvent(request):
    id = request.POST.get('cita_id')
    ids_mascotas = request.user.cliente.mascota_set.values_list('id', flat=True)

    event = get_object_or_404(Citas, id=id, idM_id__in=ids_mascotas)
    
    if request.method == 'POST':  
        event.delete()
        return redirect('calendar')  
    else:
        messages.error(request, 'No se puede eliminar la mascota de esta forma.')

def generate_events(citas):
    """Genera eventos para el calendario a partir de las citas."""
    events = []
    for cita in citas:
        start_datetime = datetime.combine(cita.fecha, cita.hora)
        end_datetime = start_datetime + timedelta(hours=1)

        events.append({
            'id': cita.id,
            'start': start_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
            'end': end_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
            'title': f'Cita: {cita.nombre}',
            'description': cita.motivo,
            'extraParams': {
                'accepted': cita.aceptada,
                'type': cita.tipo,
                'mascota': Mascota.objects.get(id=cita.idM_id).nombre,
            },
        })
    return events


@login_required
def myPets(request):
    if Cliente.objects.filter(dni=request.user).exists():
        try:
            client = Cliente.objects.get(dni=request.user)

            pets = Mascota.objects.filter(dni=client)

            return render(request, 'clinica/mascotas.html', {'pets': pets})
        except Cliente.DoesNotExist:
            return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
    else:
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

@login_required
def addPet(request):
    if request.method == 'POST':
        form = MascotaForm(request.POST, request.FILES)
        
        if form.is_valid():
            cliente = Cliente.objects.get(dni=request.user)

            historial_medico = HistorialMedico.objects.create()

            mascota = form.save(commit=False)
            mascota.dni = cliente
            mascota.idH = historial_medico
            mascota.save()
            messages.success(request, 'La mascota ha sido creada correctamente.')
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, f"Error en {field.label}: {error}")
        return redirect('myPets')

@login_required
def deletePet(request, id):
    mascota = get_object_or_404(Mascota, id=id, dni=request.user.dni)
    
    if request.method == 'POST':  
        mascota.delete()
        messages.success(request, 'La mascota ha sido eliminada correctamente.')
        return redirect('myPets')  
    else:
        messages.error(request, 'No se ha podido eliminar la mascota')

@login_required
def profile(request):
    usuario = Usuario.objects.filter(dni=request.user.dni).first()
    if usuario:
        if Cliente.objects.filter(dni=request.user.dni).exists():
            layout = "clinica/layout_cliente.html"
        elif Veterinario.objects.filter(dni=request.user.dni).exists():
            layout = "clinica/layout_veterinario.html"
            
        return render(request, 'clinica/perfilUsuario.html', {'usuario': usuario, 'layout': layout}) 

@login_required
def editProfile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Tu perfil ha sido actualizado correctamente.")
            return redirect('profile')
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, f"Error en {field.label}: {error}")

        return redirect('profile')  

    return render(request, 'clinica/perfilUsuario.html', {'usuario': request.user})

@login_required
def myAppointments(request):
    layout = "" 
    if Cliente.objects.filter(dni=request.user).exists():
        layout = "clinica/layout_cliente.html"
    elif Veterinario.objects.filter(dni=request.user).exists():
        layout = "clinica/layout_veterinario.html"
    return render(request, 'clinica/citas.html', {'layout': layout}) 

@login_required
def myRequests(request):
    return render(request, 'clinica/solicitudes.html') 