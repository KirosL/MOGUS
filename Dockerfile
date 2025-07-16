# Usa una imagen base oficial con Python y las dependencias necesarias
FROM python:3.11-slim

# Instala dependencias del sistema para WeasyPrint
RUN apt-get update && apt-get install -y \
    build-essential \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libjpeg-dev \
    libxml2 \
    libxslt1.1 \
    libssl-dev \
    libopenjp2-7 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto
COPY . .

# Instala dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto (lo usará Railway con $PORT)
EXPOSE 8000

# Comando para ejecutar tu aplicación
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app.app:crear_app", "--factory"]
