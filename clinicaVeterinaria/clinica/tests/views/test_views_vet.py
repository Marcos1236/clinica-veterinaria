from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from ...models import CodigoRegistro, Cliente, Veterinario, Usuario, Mascota, Citas
from datetime import datetime

class VetViewTest(TestCase):
    def setUp(self):   
        self.client = Client()
        User = get_user_model()
        
        # Crear un veterinario
        self.vet_user = User.objects.create_user(username='vetuser', password='123456789')
        self.vet_user.is_staff = True 
        self.vet_user.save()
        self.vet = Veterinario.objects.create(dni=self.vet_user)

        self.client.login(username='vetuser', password='123456789')
          

    def test_access_register_veterinarian(self): 
        response = self.client.get(reverse('registerVet'))  
        print("GET status code:", response.status_code) 

        if response.status_code == 302:
            print("Redireccionado a:", response['Location'])  

        if response.status_code == 200:
            self.assertTemplateUsed(response, 'clinica/registroVeterinario.html') 

        response = self.client.post(reverse('registerVet'), {
            'username': 'new1vetuser',
            'password1': 'vetpassword123',
            'password2': 'vetpassword123',
            'dni': '98765432X',
            'first_name': 'Nuevo',
            'last_name': 'Veterinario',
            'email': 'newvet@test.com'
        })
        if response.context and 'form' in response.context:
            print("Errores en el formulario:", response.context['form'].errors)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('calendar'))  
        self.assertFalse(Usuario.objects.filter(username='new1vetuser').exists())


    def test_view_requests(self):
        response = self.client.get(reverse('myRequests'))  
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clinica/solicitudes.html') 



