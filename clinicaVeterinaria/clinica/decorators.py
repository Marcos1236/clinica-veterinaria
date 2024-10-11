from django.http import HttpResponseForbidden
from .models import Cliente, Veterinario

# Decorador para clientes
def es_cliente(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and Cliente.objects.filter(user=request.user).exists():
            return func(request, *args, **kwargs)
        return HttpResponseForbidden("No tienes acceso a esta sección.")
    return wrapper

# Decorador para veterinarios
def es_veterinario(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and Veterinario.objects.filter(user=request.user).exists():
            return func(request, *args, **kwargs)
        return HttpResponseForbidden("No tienes acceso a esta sección.")
    return wrapper