from django.db import models

# Modelo de Usuario
class Usuario(models.Model):
    dni = models.CharField(max_length=15, primary_key=True)
    nombre = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    tfno = models.CharField(max_length=15)
    direccion = models.CharField(max_length=255)
    fecha_registro = models.DateTimeField()

    def __str__(self):
        return self.nombre

# Modelo de Veterinario
class Veterinario(models.Model):
    dni = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    especialidad = models.CharField(max_length=100)
    hora_entrada = models.TimeField()
    hora_salida = models.TimeField()

    def __str__(self):
        return f"{self.dni.nombre} - {self.especialidad}"

# Modelo de Cliente
class Cliente(models.Model):
    dni = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.dni.nombre


# Modelo de HistorialMedico
class HistorialMedico(models.Model):
    id = models.CharField(max_length=15, primary_key=True)
    medicacion = models.CharField(max_length=255)
    descripcion = models.TextField()

    def __str__(self):
        return f"Historial {self.idM.nombre} - {self.medicacion}"


# Modelo de Mascota
class Mascota(models.Model):
    id = models.CharField(max_length=15, primary_key=True)
    dni = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    idH= models.ForeignKey(HistorialMedico, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    edad = models.IntegerField()
    raza = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

# Modelo de Citas
class Citas(models.Model):

    TIPO_CONSULTA = {
        "U": "Urgente",
        "R": "Rutinaria",
    }

    id = models.CharField(max_length=15, primary_key=True)
    idM = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    dni = models.ForeignKey(Veterinario, on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    motivo = models.CharField(max_length=255)
    aceptada = models.BooleanField()
    tipo = models.CharField(max_length=1, choices=TIPO_CONSULTA)

    def __str__(self):
        return f"Cita: {self.id} - {self.motivo}"
