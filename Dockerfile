FROM python:3.9-slim

# 1. Instalar dependencias del sistema (CORREGIDO: libgl1 en vez de libgl1-mesa-glx)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# 2. Copiar el archivo de requisitos
COPY ./requirements.txt /code/requirements.txt

# 3. TRUCO DE TAMAÑO: Instalar primero PyTorch versión CPU (Ahorra ~700MB)
# Si dejas que requirements.txt lo instale solo, bajará la versión GPU gigante.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r /code/requirements.txt

# 4. Copiar el código de la app
COPY ./app /code/app

# 5. Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]