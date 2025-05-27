# Usa una imagen base de PHP con FPM (FastCGI Process Manager) para servir la aplicación a través de Nginx
FROM php:8.2-fpm-alpine

# Instala dependencias del sistema necesarias para Laravel y las extensiones de PHP
RUN apk add --no-cache \
    git \
    curl \
    zip \
    unzip \
    libpng-dev \
    libjpeg-turbo-dev \
    freetype-dev \
    libxml2-dev \
    icu-dev \
    libzip-dev \
    oniguruma-dev \
    g++ \
    make \
    autoconf \
    curl-dev \
    && docker-php-ext-install -j$(nproc) \
        pdo_mysql \
        mbstring \
        exif \
        pcntl \
        bcmath \
        gd \
        fileinfo \
        curl \
        xml \
        intl \
        zip \
    # Limpia el cache de apk
    && rm -rf /var/cache/apk/*

# Instala Composer globalmente
COPY --from=composer:latest /usr/bin/composer /usr/local/bin/composer

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /var/www/html

# Copia los archivos de composer primero para aprovechar el cache de Docker
# Se asume que composer.lock está en la raíz de apiEstudiantes
COPY composer.json composer.lock ./

# Instala las dependencias de PHP usando Composer
# --no-dev para no instalar dependencias de desarrollo (para imágenes de producción)
# --no-interaction para evitar preguntas interactivas
# --prefer-dist para descargar paquetes desde dist (más rápido)
# --optimize-autoloader para optimizar el autoloader
# --no-scripts para evitar la ejecución de scripts post-install aquí (se ejecutan explícitamente después)
RUN if [ -f composer.json ]; then \
        composer install --no-dev --no-interaction --prefer-dist --optimize-autoloader --no-scripts; \
    fi

# Copia el resto del código de la aplicación Laravel
# Asegúrate de tener un archivo .dockerignore en apiEstudiantes/ para excluir archivos sensibles como .env
COPY . .

# Ejecuta los scripts post-install de composer (solo el necesario)
# Esto es importante para que Laravel descubra sus paquetes y optimice el autoloader
RUN composer run-script post-autoload-dump

# Establece los permisos correctos para los directorios de storage y bootstrap/cache
# Esto es crucial para que Laravel pueda escribir logs, cache, etc.
RUN chown -R www-data:www-data /var/www/html \
    && chmod -R 755 /var/www/html \
    && chmod -R 775 storage bootstrap/cache

# Define un Healthcheck para que Docker sepa si el contenedor está saludable
# Verifica si el proceso php-fpm está corriendo
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD ["php-fpm", "-t"] || exit 1

# Expone el puerto 9000 que usa PHP-FPM por defecto
EXPOSE 9000

# El comando por defecto para iniciar PHP-FPM
CMD ["php-fpm"]
