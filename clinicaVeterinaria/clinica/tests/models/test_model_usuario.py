from django.test import TestCase
from ...models import Usuario
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError

class UsuarioModelTests(TestCase):

    def test_creacion_usuario(self):
        usuario = Usuario.objects.create_user(
            dni='12345678',
            username='testuser',
            email='test@test.com',
            password='testpassword',
            first_name='Test',
            last_name='User',
            telefono='1234567890',
            direccion='123 Test St',
            ciudad='Test City',
            pais='Test Country',
            codigo_postal='12345'
        )
        self.assertIsInstance(usuario, Usuario)
        self.assertEqual(usuario.dni, '12345678')

    def test_creacion_usuario_sin_dni(self):
        with self.assertRaises(ValidationError):
         usuario = Usuario.objects.create_user(
            dni='',
            username='testuser',
            email='test@test.com',
            password='testpassword',
            first_name='Test',
            last_name='User',
            telefono='1234567890',
            direccion='123 Test St',
            ciudad='Test City',
            pais='Test Country',
            codigo_postal='12345'
        )
         usuario.full_clean() 

    def test_str(self):
        usuario = Usuario.objects.create_user(username='testuser', first_name='Test')
        self.assertEqual(str(usuario), 'Test')


    def test_password_encriptado(self):
        usuario = Usuario.objects.create_user(username='testuser', password='testpassword')
        self.assertTrue(check_password('testpassword', usuario.password))

    def test_creacion_usuario_email_invalido(self):
        with self.assertRaises(ValidationError):
            usuario = Usuario.objects.create_user(
                dni='12345678',
                username='testuser',
                email='invalid-email',  
                password='testpassword',
                first_name='Test',
                last_name='User',
                telefono='1234567890',
                direccion='123 Test St',
                ciudad='Test City',
                pais='Test Country',
                codigo_postal='12345'
            )
            usuario.full_clean()  


    def test_actualizacion_usuario(self):
        usuario = Usuario.objects.create_user(
            dni='12345678',
            username='testuser',
            email='test@test.com',
            password='testpassword',
            first_name='Test',
            last_name='User',
            telefono='1234567890',
            direccion='123 Test St',
            ciudad='Test City',
            pais='Test Country',
            codigo_postal='12345'
        )
        usuario.first_name = 'NewTest'
        usuario.save()
        self.assertEqual(usuario.first_name, 'NewTest')

    def test_dni_unico(self):
        usuario1 = Usuario.objects.create(dni='12345678A')
        usuario2 = Usuario(dni='12345678A')
        
        with self.assertRaises(ValidationError):
            usuario2.full_clean()
