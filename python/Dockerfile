# Usa una imagen base ligera de Python
FROM python:3.9-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de dependencias
COPY requirements.txt .

# Instala las dependencias
# Asegúrate de que 'gunicorn' esté listado en requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el contenido de la app
# Esto copiará la carpeta 'login_app' (y todo lo demás dentro de 'python/') a '/app/'
COPY . .

# Expone el puerto que Flask usará
EXPOSE 5000

# Comando para lanzar la app con Gunicorn
# 'login_app.app:app' indica a Gunicorn que busque la instancia de Flask 'app'
# dentro del módulo 'app' que se encuentra en el paquete 'login_app'.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "login_app.app:app"]
