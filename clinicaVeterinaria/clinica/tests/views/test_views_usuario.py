from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from ...models import CodigoRegistro, Cliente, Veterinario, Usuario, Mascota, Citas
from datetime import datetime

class UsuarioViewTest(TestCase):
    def setUp(self):
        self.client = Client()

        User = get_user_model() 
        self.user = User.objects.create_user(dni='12345678Z', username='testuser', password='12345')
        self.cliente = Cliente.objects.create(dni=self.user)

        self.vet_user = User.objects.create_user(username='vetuser', password='12345')
        self.vet = Veterinario.objects.create(dni=self.vet_user)

        self.codigo_registro = CodigoRegistro.objects.create(codigo='ABC12345', utilizado=False)
        
        self.mascota = Mascota.objects.create(
            dni=self.cliente,
            nombre='Rex',
            edad=5,
            raza='Labrador',
            descripcion='Perro amistoso',
            foto=None 
        )


    def test_index_view(self):
        # Prueba sin autenticación
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clinica/pantallaCarga.html')

        # Prueba con usuario autenticado
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('calendar'))

    def test_custom_admin_view(self):
        # Login sin ser admin
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('custom_admin'))
        self.assertEqual(response.status_code, 302) 
        self.assertRedirects(response, '/calendar/')

        response = self.client.post(reverse('custom_admin'), {'cantidad': 1})
        self.assertEqual(response.status_code, 302)  
        self.assertRedirects(response, '/calendar/')

        self.client.logout()

        # Login como admin
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='testuser', password='12345')

        response = self.client.post(reverse('custom_admin'), {'cantidad': 1})
        self.assertEqual(response.status_code, 302)  
        self.assertTrue(CodigoRegistro.objects.filter(utilizado=False).exists())

    def test_register_client_view(self):
        # Acceso como usuario no autenticado
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('registerClient'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('calendar'))

        self.client.logout()
        # Acceso como usuario no autenticado
        response = self.client.get(reverse('registerClient'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clinica/registroCliente.html')

        # Registro de cliente
        response = self.client.post(reverse('registerClient'), {
            'username': 'newuser',
            'password1': 'admin3211',
            'password2': 'admin3211',
            'email': 'test@test.com',
            'dni': '12345678L',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'telefono': '123456789',
            'direccion': 'Calle X',
            'ciudad': 'Ciudad X',
            'pais': 'España',
            'codigo_postal': '12345',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('calendar'))
        self.assertTrue(Usuario.objects.filter(username='newuser').exists())


    def test_access_client_profile_view(self):
        User = get_user_model() 
        self.user = User.objects.create_user(dni='123456278Z', username='testuser2', password='123456789')
        self.cliente = Cliente.objects.create(dni=self.user)

        # Asegúrate de que el usuario puede acceder a su perfil
        self.client.login(username='testuser2', password='123456789')
        response = self.client.get(reverse('profile'))  
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clinica/perfilUsuario.html')  

