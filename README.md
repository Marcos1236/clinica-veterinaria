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
    git clone https://github.com/Marcos1236/clinica-veterinaria.git

2. Asegúrate de que Docker y Docker Compose estén instalados y en ejecución en tu máquina.

A partir de aquí podemos desplegar la aplicación de dos formas:

3.1 Si deseamos construir el contenedor de docker por nuestra cuenta y estamos familiarizados con estos comandos podemos construir e iniciar el contenedor con:
    docker-compose up --build

3.2 Si, por el contrario, deseamos una opción más cómoda y sencilla, podemos usar el ejecutable "ClinicaVeterinaria.exe", el cual pone en funcionamiento los contenedores, realiza
    las migraciones no aplicadas y crea un usuario administrador en caso de que no exista. Recomendamos esta opción al menos la primera vez que se ejecute la aplicación par asegurarnos
    de que todo está correctamente configurado.

4- En caso de que se desee poblar la base de datos con datos de pruebe, podemos ejecutar en el contenedor docker llamado web: 
    python manage.py loaddata clinica/fixatures/*

5. La aplicación estará disponible en http://localhost:8000.
