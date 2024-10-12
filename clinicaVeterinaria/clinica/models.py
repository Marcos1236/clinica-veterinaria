from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password

# Modelo de Usuario
class Usuario(AbstractUser):
    dni = models.CharField(max_length=15, primary_key=True)
    telefono = models.CharField(max_length=15)
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    pais = models.CharField(max_length=50)
    codigo_postal = models.CharField(max_length=10)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.first_name

# Modelo de Veterinario
class Veterinario(models.Model):
    dni = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    especialidad = models.CharField(max_length=100)
    hora_entrada = models.TimeField()
    hora_salida = models.TimeField()

    def __str__(self):
        return f"{self.dni.first_name} - {self.especialidad}"

# Modelo de Cliente
class Cliente(models.Model):
    dni = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.dni.first_name


# Modelo de HistorialMedico
class HistorialMedico(models.Model):
    id = models.AutoField(primary_key=True)
    medicacion = models.CharField(max_length=255)
    descripcion = models.TextField()

    def __str__(self):
        return f"Historial {self.idM.nombre} - {self.medicacion}"


# Modelo de Mascota
class Mascota(models.Model):
    id = models.AutoField(primary_key=True)
    dni = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    idH= models.ForeignKey(HistorialMedico, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    edad = models.IntegerField()
    raza = models.CharField(max_length=100)
    descripcion = models.TextField()
    foto = models.ImageField(upload_to='mascotas_fotos/', blank=True, null=True)

    def __str__(self):
        return self.nombre

# Modelo de Citas
class Citas(models.Model):

    TIPO_CONSULTA = {
        "U": "Urgente",
        "R": "Rutinaria",
    }

    id = models.AutoField(primary_key=True)
    idM = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    dni = models.ForeignKey(Veterinario, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    fecha = models.DateTimeField()
    hora = models.TimeField()
    motivo = models.CharField(max_length=255)
    aceptada = models.BooleanField(default=False)
    tipo = models.CharField(max_length=1, choices=TIPO_CONSULTA)

    def __str__(self):
        return f"Cita: {self.id} - {self.motivo}"

class CodigoRegistro(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    utilizado = models.BooleanField(default=False)

    def __str__(self):
        return self.codigo