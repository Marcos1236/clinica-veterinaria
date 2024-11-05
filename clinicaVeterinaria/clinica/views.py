from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from channels.testing import WebsocketCommunicator
from django.contrib import messages
from .forms import *
from .models import *
from django.http import HttpResponseForbidden
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from collections import Counter
import random
import string
import json

FECHA_HORA_VALIDA = 0
FECHA_HORA_ANTIGUA = 1
VET_NO_DISPONIBLES = 2

def index(request):
    if request.user.is_authenticated:
        return redirect('calendar')
    return render(request, "clinica/pantallaCarga.html")

@staff_member_required
def custom_admin(request):

    if request.method == 'POST':
        form = GenerarCodigoForm(request.POST)
        if form.is_valid():
            cantidad = form.cleaned_data['cantidad']
            for _ in range(cantidad):
                
                codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                CodigoRegistro.objects.create(codigo=codigo)
            messages.success(request, f'Se han generado {cantidad} códigos nuevos.')
            return redirect('custom_admin')
        else:
            showErrors(request, form)
    else:
        form = GenerarCodigoForm()
    
        dni_clientes = Cliente.objects.values_list('dni', flat=True)
        clientes = Usuario.objects.filter(dni__in=dni_clientes)
        paginator = Paginator(clientes, 10)  
        page_number = request.GET.get('page')
        usuarios_clientes = paginator.get_page(page_number)

        dni_vet = Veterinario.objects.values_list('dni', flat=True)
        veterinarios = Veterinario.objects.filter(dni__in=dni_vet)
        paginator = Paginator(veterinarios, 10)  
        page_number = request.GET.get('page')
        usuarios_Veterinarios= paginator.get_page(page_number)

        total_clients = Cliente.objects.count()
        total_vets = Veterinario.objects.count()
        average_pets_per_client = Mascota.objects.count() / total_clients if total_clients > 0 else 0

        citas = Citas.objects.all()
        citas_por_dia = Counter([cita.fecha.date().weekday() for cita in citas]) 
        days_data = [citas_por_dia.get(i, 0) for i in range(7)]

        citas_por_mes = Counter([cita.fecha.date().month for cita in citas])
        months_data = [citas_por_mes.get(i, 0) for i in range(1, 13)]

        codigos = CodigoRegistro.objects.all()

    context = {
        'index_title': 'Estadísticas Administrativas',
        'average_pets_per_client': average_pets_per_client,
        'total_clients': total_clients,
        'total_vets': total_vets,
        'days_data': json.dumps(days_data),
        'months_data': json.dumps(months_data),
        'form': form, 
        'codigos': codigos,
        'clientes': usuarios_clientes,
        'veterinarios' : usuarios_Veterinarios,
    }

    return render(request, 'clinica/custom_admin.html', context)

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
        form_veterinario = RegistroVetForm(request.POST)

        codigo_ingresado = request.POST.get('codigo_registro')

        try:
            codigo = CodigoRegistro.objects.get(codigo=codigo_ingresado, utilizado=False)
        except CodigoRegistro.DoesNotExist:
            messages.error(request, 'Código de registro inválido o ya utilizado.')
            return render(request, 'clinica/registroVeterinario.html', {'form': form})

        if form.is_valid() and form_veterinario.is_valid():
            usuario = form.save()
            especialidad = form_veterinario.cleaned_data.get('especialidad')
            vet = Veterinario(dni=usuario, especialidad=especialidad)
            vet.save()

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

    if user.is_superuser:
        return redirect('custom_admin')

    if Cliente.objects.filter(dni=request.user).exists():
        mascotas = Mascota.objects.filter(dni=user.dni)
        citas = Citas.objects.filter(idM__in=mascotas)

        horas_jornada = []
        vets = []
        allVets = Veterinario.objects.all()

        for vet in allVets:
            user = Usuario.objects.get(dni=vet.dni_id)
            nombre = user.first_name
            apellidos = user.last_name

            jornada_inicio = datetime.combine(timezone.now().date(), vet.hora_entrada)
            jornada_fin = datetime.combine(timezone.now().date(), vet.hora_salida)
            
            horas_jornada = [
                (jornada_inicio + timedelta(hours=i)).strftime('%H:%M')
                for i in range(int((jornada_fin - jornada_inicio).total_seconds() // 3600) + 1)
            ]
            
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
            'horas' :horas_jornada,
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
            cita = Citas.objects.get(id=request.POST.get('cita_id'))  
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

            mascota = form.save(commit=False)
            mascota.dni = cliente
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
        esCliente = True
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
                    "tipo": cita.tipo,
                    "esCliente" : esCliente
                })
    elif Veterinario.objects.filter(dni=user.dni).exists():
        citas = Citas.objects.filter(dni=user.dni).order_by('fecha', 'hora')
        esCliente = False
        for cita in citas:
            citas_usuario.append({
                "citas_id": cita.id,
                "nombre": cita.nombre,
                "fecha": cita.fecha,
                "hora": cita.hora,
                "motivo": cita.motivo,
                "aceptada": cita.aceptada,
                "tipo": cita.tipo,
                "tratamiento" : cita.tratamiento,
                "medicacion" : cita.medicacion,
                "esCliente" : esCliente
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
    if '__all__' in form.errors:
        for error in form.errors['__all__']:
            messages.error(request, f"Error: {error}")

    for field in form:
        for error in field.errors:
            
            messages.error(request, f"Error en {field.label}: {error}")
    


@login_required
def historialMedico(request, id):
    user = request.user

    if Cliente.objects.filter(dni=user.dni).exists():
        now = timezone.now()
        citas = Citas.objects.filter(idM=id, fecha__lt=now)

        mascota = get_object_or_404(Mascota, id=id)
    elif Veterinario.objects.filter(dni=user.dni).exists():
        return redirect('citas')
    
    context = {
        'mascota': mascota,
        'citas': citas,
        'usuario' : user,
    }
    
    return render(request, 'clinica/historialMedico.html', context)

@login_required
def modificarHistorial(request):
    user = request.user

    if request.method == 'POST':
        if Veterinario.objects.filter(dni=user.dni).exists():
            cita_id = request.POST.get("cita_id")
            cita = get_object_or_404(Citas, id=cita_id)
            
            cita.tratamiento = request.POST.get("tratamiento")
            cita.medicacion = request.POST.get("medicacion")
            cita.save()
            
            messages.success(request, "Historial medico actualizado exitosamente")
            return redirect('myAppointments')
        elif Cliente.objects.filter(dni=user.dni).exists():
            return redirect('citas')
        
