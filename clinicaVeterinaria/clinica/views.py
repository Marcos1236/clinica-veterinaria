from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.views.generic import TemplateView
from .forms import *
from .models import *
from .decorators import es_cliente, es_veterinario
from django.http import HttpResponse, HttpResponseForbidden


# Create your views here.
def index(request):
    return render(request, "clinica/pantallaCarga.html")

def registerClient(request):
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

def login(request):
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

def calendar(request):
    if request.user.is_authenticated:
        if Cliente.objects.filter(dni=request.user).exists():
            return render(request, 'clinica/calendario_cliente.html') 
        elif Veterinario.objects.filter(dni=request.user).exists():
            return render(request, 'clinica/calendario_veterinario.html') 
    else:
        return redirect('login')  

@login_required
def myPets(request):
    if request.method == 'POST':
        form = MascotaForm(request.POST, request.FILES)
        
        if form.is_valid():
            cliente = Cliente.objects.get(dni=request.user)

            historial_medico = HistorialMedico.objects.create()

            mascota = form.save(commit=False)
            mascota.dni = cliente
            mascota.idH = historial_medico
            mascota.save()

            return redirect('myPets')
        else:
            return render(request, 'clinica/mascotas.html', {'form': form})

    elif request.method == 'GET':
        if Cliente.objects.filter(dni=request.user).exists():
            try:
                client = Cliente.objects.get(dni=request.user)

                pets = Mascota.objects.filter(dni=client)

                return render(request, 'clinica/mascotas.html', {'pets': pets})
            except Cliente.DoesNotExist:
                return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
        else:
            return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

def deletePet(request, id):
    if request.user.is_authenticated:
        mascota = get_object_or_404(Mascota, id=id, dni=request.user.dni)
        
        if request.method == 'POST':  
            mascota.delete()
            messages.success(request, 'La mascota ha sido eliminada correctamente.')
            return redirect('myPets')  
        else:
            messages.error(request, 'No se puede eliminar la mascota de esta forma.')
    else:
        messages.error(request, 'Debes estar autenticado para eliminar una mascota.')
        return redirect('login')

def profile(request):
    if request.user.is_authenticated:
        usuario = Usuario.objects.filter(dni=request.user.dni).first()
        if usuario:
            print(usuario.first_name)
            return render(request, 'clinica/perfilUsuario.html', {'usuario': usuario}) 
    else:
        return redirect('login')

@login_required
def editProfile(request):
    if request.method == 'POST':
        usuario = request.user

        usuario.first_name = request.POST.get('first_name')
        usuario.email = request.POST.get('email')
        usuario.telefono = request.POST.get('telefono')
        usuario.direccion = request.POST.get('direccion')

        usuario.save()

        messages.success(request, "Tu perfil ha sido actualizado correctamente.")

        return redirect('perfil')  

    return render(request, 'clinica/perfilUsuario.html', {'usuario': request.user})
    
def myAppointments(request):
    if request.user.is_authenticated:   
        layout = "" 
        if Cliente.objects.filter(dni=request.user).exists():
            layout = "clinica/layout_cliente.html"
        elif Veterinario.objects.filter(dni=request.user).exists():
            layout = "clinica/layout_veterinario.html"
        return render(request, 'clinica/citas.html', {'layout': layout}) 
    else:
        return redirect('login')
