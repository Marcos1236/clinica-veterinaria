# Clínica Veterinaria

¡Bienvenido a la aplicación de Clínica Veterinaria! Esta aplicación permite gestionar la interacción entre clientes y veterinarios de manera eficiente. Los clientes pueden registrar sus mascotas, reservar citas y chatear con veterinarios disponibles en tiempo real.

## Funcionalidades

- **Clientes**: Pueden crearse una cuenta, registrar mascotas y reservar citas para sus mascotas.
- **Veterinarios**: Pueden registrarse y gestionar citas con los clientes.
- **Citas**: Los clientes pueden reservar citas para sus mascotas, y los veterinarios pueden aceptarlas.
- **Chat**: Los clientes pueden chatear con veterinarios activos, facilitando la comunicación directa.

## Requisitos

- Docker
- Docker Compose

## Ejecución

Para ejecutar la aplicación, sigue estos pasos:

1. Clona este repositorio en tu máquina local:
   git clone https://tu-repositorio.git
   cd clinicaVeterinaria
2. Asegúrate de que Docker y Docker Compose estén instalados y en ejecución en tu máquina.

3. Construye y lanza los contenedores usando docker-compose:
    docker-compose up --build
4. La aplicación estará disponible en http://localhost:8000.
