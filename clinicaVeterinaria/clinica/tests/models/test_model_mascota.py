from django.test import TestCase
from ...models import Usuario
from ...models import Mascota
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from ...forms import MascotaForm

class mascotaModelTests(TestCase):

    from django.test import TestCase
from ...models import Usuario, Cliente, Mascota
from django.core.exceptions import ValidationError

class MascotaModelTests(TestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            dni='12345678',
            username='clientuser',
            email='client@test.com',
            password='testpassword',
            first_name='Client',
            last_name='User',
            telefono='1234567890',
            direccion='789 Client St',
            ciudad='Client City',
            pais='Client Country',
            codigo_postal='54321'
        )
        self.cliente = Cliente.objects.create(dni=self.usuario)

    def test_creacion_mascota(self):
        mascota = Mascota.objects.create(
            dni=self.cliente,
            nombre='Rex',
            edad=5,
            raza='Labrador',
            descripcion='Perro amistoso',
            foto=None  
        )
        self.assertIsInstance(mascota, Mascota)
        self.assertEqual(mascota.nombre, 'Rex')
        self.assertEqual(mascota.edad, 5)
        self.assertEqual(mascota.raza, 'Labrador')
        self.assertEqual(mascota.descripcion, 'Perro amistoso')

    def test_str_mascota(self):
        mascota = Mascota.objects.create(
            dni=self.cliente,
            nombre='Rex',
            edad=5,
            raza='Labrador',
            descripcion='Perro amistoso',
            foto=None  
        )
        self.assertEqual(str(mascota), 'Rex')
       

    def test_edad_negativa(self):
        with self.assertRaises(ValidationError):
            mascota = Mascota(dni=self.cliente, nombre='Rex', edad= -1, raza='Labrador', descripcion='Perro amistoso')
            mascota.full_clean()  

    def test_raza_vacia(self):
        with self.assertRaises(ValidationError):
            mascota = Mascota(dni=self.cliente, nombre='Rex', edad=5, raza='', descripcion='Perro amistoso')
            mascota.full_clean()  

    def test_raza_no_valida(self):
        form_data = {
            'nombre': 'Rex',
            'edad': 5,
            'raza': 'persa',  
            'descripcion': 'Perro amistoso',
        }
        form = MascotaForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('raza', form.errors)  


