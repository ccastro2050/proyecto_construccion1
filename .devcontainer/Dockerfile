# ==============================================================
# Contenedor de desarrollo: Python 3.12 + dependencias del proyecto
# ==============================================================
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        git curl nano \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python en la imagen (arranque rapido)
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /workspace
