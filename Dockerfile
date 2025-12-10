FROM python:3.9-slim

# CORRECCIÓN AQUÍ: Cambiamos libgl1-mesa-glx por libgl1
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Copiar requirements e instalar
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copiar el código de la app
COPY ./app /code/app

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]