# Usar una imagen base de Python
FROM python:3.11

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de requerimientos
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Exponer el puerto que usará Nginx
EXPOSE 8000

# Comando para ejecutar el servidor Daphne
CMD ["daphne", "-u", "/tmp/daphne.sock", "clinicaVeterinaria.asgi:application"]  
