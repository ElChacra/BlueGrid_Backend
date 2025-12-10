FROM python:3.9-slim

# Instalar dependencias del sistema para OpenCV (glib)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Instalar dependencias Python
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copiar el código
COPY ./app /code/app

# Crear directorio para caché temporal de imágenes (Vital para el feedback)
RUN mkdir -p /code/temp_last_batch && chmod 777 /code/temp_last_batch

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]