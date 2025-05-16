# Usa una imagen de Python como base
FROM python:3.9-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo de requisitos (requirements.txt) al contenedor
COPY requirements.txt requirements.txt

# Instala las dependencias desde requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación al contenedor
COPY . .

# Expone el puerto en el que se ejecutará la aplicación
EXPOSE 5001

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]  # Cambia app.py por el nombre de tu archivo principal
