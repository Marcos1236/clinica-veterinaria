from django.test import TestCase
from ...models import Usuario
from ...models import Veterinario
from datetime import time
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError



class VetModelTests(TestCase):
    
    def setUp(self):
        # Crea un usuario que será utilizado para el veterinario
        self.usuario = Usuario.objects.create_user(
            dni='12345678',
            username='vetuser',
            email='vet@test.com',
            password='testpassword',
            first_name='Vet',
            last_name='User',
            telefono='1234567890',
            direccion='456 Vet St',
            ciudad='Vet City',
            pais='Vet Country',
            codigo_postal='67890'
        )

    def test_creacion_veterinario(self):
        # Crea un veterinario
        veterinario = Veterinario.objects.create(
            dni=self.usuario,
            especialidad='Cirujano',
            hora_entrada=time(8, 0),
            hora_salida=time(16, 0)
        )
        self.assertIsInstance(veterinario, Veterinario)
        self.assertEqual(veterinario.especialidad, 'Cirujano')
        self.assertEqual(veterinario.hora_entrada, time(8, 0))
        self.assertEqual(veterinario.hora_salida, time(16, 0))
    
    def test_str_veterinario(self):
        veterinario = Veterinario.objects.create(
            dni=self.usuario,
            especialidad='Cirujano'
        )
        self.assertEqual(str(veterinario), 'Vet - Cirujano')

    def test_hora_entrada_salida_por_defecto(self):
        veterinario = Veterinario.objects.create(
            dni=self.usuario,
            especialidad='Veterinario General'
        )
        self.assertEqual(veterinario.hora_entrada, time(7, 0))
        self.assertEqual(veterinario.hora_salida, time(15, 0))

    def test_especialidad_vacia(self):
        with self.assertRaises(ValidationError):
            veterinario = Veterinario(dni=self.usuario, especialidad='')
            veterinario.full_clean()  

    