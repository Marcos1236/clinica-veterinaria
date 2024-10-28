from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from channels.testing import WebsocketCommunicator
from django.contrib import messages
from django.views.generic import TemplateView
from django.http import JsonResponse
from .forms import *
from .models import *
from clinicaVeterinaria.asgi import application
from .forms import HistorialMedicoForm
from .decorators import es_cliente, es_veterinario
from django.http import HttpResponse, HttpResponseForbidden
from datetime import datetime, timedelta
from django.core.paginator import Paginator
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
                
                codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                CodigoRegistro.objects.create(codigo=codigo)
            messages.success(request, f'Se han generado {cantidad} códigos nuevos.')
            return redirect('generateCode')
        else:
            showErrors(request, form)
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

            auth_login(request, usuario) 
            messages.success(request, '¡Tu cuenta ha sido creada con éxito!')
            return redirect('calendar')  
        else:
            showErrors(request, form)

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

            form2 = RegistroVetForm(request.POST)

            if form2.is_valid():
                form2.save()
            else:
                showErrors(request, form2)

            codigo.utilizado = True
            codigo.save()

            auth_login(request, usuario) 
            messages.success(request, '¡Tu cuenta ha sido creada con éxito!')
            return redirect('calendar')
        else:
            showErrors(request, form)

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

        vets = []
        allVets = Veterinario.objects.all()

        for vet in allVets:
            user = Usuario.objects.get(dni=vet.dni_id)
            nombre = user.first_name
            apellidos = user.last_name
   
            vets.append({
                'dni_id': vet.dni_id,
                'first_name': nombre,  
                'last_name': apellidos
            })

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
            'vets': json.dumps(vets),
            'user' : request.user,
        }
        return render(request, 'clinica/calendario_cliente.html', context)

    elif Veterinario.objects.filter(dni=request.user).exists():
        citas = Citas.objects.filter(dni=user.dni)
        events = generate_events(citas)

        context = {
            'events': json.dumps(events),
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
            showErrors(request, form)
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
            showErrors(request, form)
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
    events = []
    fecha_actual = datetime.now()
    for cita in citas:
        start_datetime = datetime.combine(cita.fecha, cita.hora)
        end_datetime = start_datetime + timedelta(hours=1)

        if fecha_actual < end_datetime:
            events.append({
                'id': cita.id,
                'start': start_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
                'end': end_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
                'title': f'Cita: {cita.nombre}',
                'description': cita.motivo,
                'color': determine_color(cita),
                'extraParams': {
                    'accepted': cita.aceptada,
                    'type': cita.tipo,
                    'mascota': Mascota.objects.get(id=cita.idM_id).nombre
                },
            })
    return events

def determine_color(cita):
    fecha_inicio = datetime.combine(cita.fecha, cita.hora)
    if fecha_inicio < datetime.now(): 
        return 'gray'  
    elif cita.tipo == 'U':  
        return 'red'  
    else:
        return 'purple' 


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
            showErrors(request, form)
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
        else:
            showErrors(request, form)

    return redirect('profile')  

@login_required
def changePassword(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Tu contraseña ha sido actualizada correctamente.")
        else:
            showErrors(request, form)

    return redirect('profile') 

@login_required
def myAppointments(request):
    layout = ""
    user = request.user
    citas_usuario = []

    if Cliente.objects.filter(dni=user.dni).exists():
        layout = "clinica/layout_cliente.html"

        mascotas = Mascota.objects.filter(dni=user.dni)

        for mascota in mascotas:
            citas = Citas.objects.filter(idM=mascota).order_by('fecha', 'hora')
            for cita in citas:
                citas_usuario.append({
                    "citas_id": cita.id,
                    "nombre": cita.nombre,
                    "fecha": cita.fecha,
                    "hora": cita.hora,
                    "motivo": cita.motivo,
                    "aceptada": cita.aceptada,
                    "tipo": cita.tipo
                })
    elif Veterinario.objects.filter(dni=user.dni).exists():
        citas = Citas.objects.filter(dni=user.dni).order_by('fecha', 'hora')
        for cita in citas:
            citas_usuario.append({
                "citas_id": cita.id,
                "nombre": cita.nombre,
                "fecha": cita.fecha,
                "hora": cita.hora,
                "motivo": cita.motivo,
                "aceptada": cita.aceptada,
                "tipo": cita.tipo
            })
        layout = "clinica/layout_veterinario.html"

    fecha_actual = timezone.now()
    
    citas_pendientes = [cita for cita in citas_usuario if cita["fecha"] >= fecha_actual]
    citas_historial = [cita for cita in citas_usuario if cita["fecha"] < fecha_actual]

    paginator_pendientes = Paginator(citas_pendientes, 4) 
    page_number_pendientes = request.GET.get('pendientes_page')
    page_obj_pendientes = paginator_pendientes.get_page(page_number_pendientes)


    paginator_historial = Paginator(citas_historial, 4) 
    page_number_historial = request.GET.get('historial_page')
    page_obj_historial = paginator_historial.get_page(page_number_historial)

    context = {
        'layout': layout,
        'page_obj_pendientes': page_obj_pendientes,
        'page_obj_historial': page_obj_historial,
    }

    return render(request, "citas.html", context)

@login_required
def myRequests(request):
    if Veterinario.objects.filter(dni=request.user).exists():
        fecha_actual = timezone.now()


        citas = Citas.objects.filter(fecha__gt=fecha_actual, aceptada=False).order_by('fecha', 'hora')
        citas_usuario = Citas.objects.filter(dni=request.user.dni, fecha__gt=fecha_actual).order_by('fecha', 'hora')
        solicitudes = []

        for cita in citas:
            cita_start = datetime.combine(cita.fecha, cita.hora)

            conflicto = False
            for cita_usuario in citas_usuario:
                cita_usuario_start = datetime.combine(cita_usuario.fecha, cita_usuario.hora)
                
                if cita_start == cita_usuario_start:
                    conflicto = True
                    break
            
            if not conflicto:
                solicitudes.append(cita)                   
        
        paginator = Paginator(solicitudes, 3)  
        page_number = request.GET.get('page')  
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj,
        }

        return render(request, 'clinica/solicitudes.html', context)
    else:
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('calendar')
    
@login_required
def acceptRequest(request, id):
    if not Veterinario.objects.filter(dni=request.user).exists():
        messages.error(request, 'No tienes permiso para aceptar citas.')
        return redirect('calendar') 

    cita = get_object_or_404(Citas, id=id)
    cita.aceptada = True
    cita.dni_id = request.user.dni
    cita.save()

    messages.success(request, 'Cita aceptada exitosamente.')
    return redirect('myRequests') 

def rejectRequest(request):
    if not Veterinario.objects.filter(dni=request.user).exists():
        messages.error(request, 'No tienes permiso para aceptar citas.')
        return redirect('calendar') 
    
    id = request.POST.get('cita_id')
    cita = get_object_or_404(Citas, id=id)
    
    if request.method == 'POST':  
        cita.dni = None
        cita.aceptada = False
        cita.save()
        return redirect('calendar')  
    else:
        messages.error(request, 'No se puede eliminar la mascota de esta forma.')

def showErrors(request, form):
    for field in form:
        for error in field.errors:
            messages.error(request, f"Error en {field.label}: {error}")


@login_required
def historialMedico(request, mascota_id):
    mascota = get_object_or_404(Mascota, id=mascota_id)
    historial = historialMedico.html
    es_veterinario = request.user.groups.filter(name='Veterinarios').exists()
    
    context = {
        'mascota': mascota,
        'historial': historial,
        'es_veterinario': es_veterinario
    }
    
    return render(request, template, context)

@login_required
def modificar_historial_medico(request, historial_id):
    historial = get_object_or_404(HistorialMedico, id=historial_id)

    if request.method == 'POST':
        form = HistorialMedicoForm(request.POST, instance=historial)
        if form.is_valid():
            form.save()
            messages.success(request, 'El historial médico ha sido actualizado correctamente.')
            return redirect('historial_detalle', historial_id=historial.id)  # Redirige a la vista de detalle del historial
        else:
            messages.error(request, 'Error al actualizar el historial médico.')
    else:
        form = HistorialMedicoForm(instance=historial)

    return render(request, 'historialMedico.html', {'form': form, 'historial': historial})

