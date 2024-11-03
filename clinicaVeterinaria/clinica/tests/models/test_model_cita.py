from django.test import TestCase
from ...models import Usuario, Cliente, Mascota, Veterinario, Citas
from django.core.exceptions import ValidationError
from django.utils import timezone

class CitasModelTests(TestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            dni='12345678',
            username='vetuser',
            email='vet@test.com',
            password='testpassword',
            first_name='Vet',
            last_name='User',
            telefono='1234567890',
            direccion='123 Vet St',
            ciudad='Vet City',
            pais='Vet Country',
            codigo_postal='54321'
        )
        self.cliente = Cliente.objects.create(dni=self.usuario)
        self.veterinario = Veterinario.objects.create(dni=self.usuario, especialidad='General')

        self.mascota = Mascota.objects.create(
            dni=self.cliente,
            nombre='Rex',
            edad=5,
            raza='Labrador',
            descripcion='Perro amistoso',
            foto=None 
        )

    def test_creacion_cita(self):
        cita = Citas.objects.create(
            idM=self.mascota,
            dni=self.veterinario,
            nombre='Cliente Test',
            fecha=timezone.now() + timezone.timedelta(days=1),
            hora=timezone.now().time(),
            motivo='Chequeo general',
            aceptada=False,
            tipo='R'
        )
        self.assertIsInstance(cita, Citas)
        self.assertEqual(cita.nombre, 'Cliente Test')
        self.assertEqual(cita.motivo, 'Chequeo general')
        self.assertFalse(cita.aceptada)

    def test_str_cita(self):
        cita = Citas.objects.create(
            idM=self.mascota,
            dni=self.veterinario,
            nombre='Cliente Test',
            fecha=timezone.now() + timezone.timedelta(days=1),
            hora=timezone.now().time(),
            motivo='Chequeo general',
            aceptada=False,
            tipo='R'
        )
        self.assertEqual(str(cita), f"Cita: {cita.id} - Chequeo general")

    def test_fecha_anterior(self):
        with self.assertRaises(ValidationError):
            cita = Citas(
                idM=self.mascota,
                dni=self.veterinario,
                nombre='Cliente Test',
                fecha=timezone.now() - timezone.timedelta(days=1),
                hora=timezone.now().time(),
                motivo='Chequeo general',
                aceptada=False,
                tipo='R'
            )
            cita.full_clean() 

    def test_tipo_consulta_invalido(self):
        with self.assertRaises(ValidationError):
            cita = Citas(
                idM=self.mascota,
                dni=self.veterinario,
                nombre='Cliente Test',
                fecha=timezone.now() + timezone.timedelta(days=1),
                hora=timezone.now().time(),
                motivo='Chequeo general',
                aceptada=False,
                tipo='X' #invalido
            )
            cita.full_clean()  

    def test_sin_nombre(self):
        with self.assertRaises(ValidationError):
            cita = Citas(
                idM=self.mascota,
                dni=self.veterinario,
                nombre='',  # Nombre vacío
                fecha=timezone.now() + timezone.timedelta(days=1),
                hora=timezone.now().time(),
                motivo='Chequeo general',
                aceptada=False,
                tipo='R'
            )
            cita.full_clean() 

    def test_cita_no_aceptada_por_defecto(self):
        cita = Citas.objects.create(
            idM=self.mascota,
            dni=self.veterinario,
            nombre='Cliente Test',
            fecha=timezone.now() + timezone.timedelta(days=1),
            hora=timezone.now().time(),
            motivo='Chequeo general',
            tipo='R'
        )

        self.assertFalse(cita.aceptada)

    def test_cita_aceptada(self):
        cita = Citas.objects.create(
            idM=self.mascota,
            dni=self.veterinario,
            nombre='Cliente Test',
            fecha=timezone.now() + timezone.timedelta(days=1),
            hora=timezone.now().time(),
            motivo='Chequeo general',
            aceptada=True,
            tipo='R'
        )

        self.assertTrue(cita.aceptada)

    def test_cita_aceptada_y_rechazada(self):
        cita = Citas.objects.create(
            idM=self.mascota,
            dni=self.veterinario,
            nombre='Cliente Test',
            fecha=timezone.now() + timezone.timedelta(days=1),
            hora=timezone.now().time(),
            motivo='Chequeo general',
            aceptada=True,
            tipo='R'
        )

        cita.aceptada = False
        cita.save()
        self.assertFalse(cita.aceptada)