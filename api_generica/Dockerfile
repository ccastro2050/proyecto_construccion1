# ==============================================================
# Dockerfile de la API Generica (FastAPI)
#
# Un Dockerfile es la "receta" para construir la imagen del
# contenedor: parte de una imagen base (Python 3.12) y le agrega
# lo que la aplicacion necesita para ejecutarse.
# ==============================================================
FROM python:3.12-slim

# --------------------------------------------------------------
# Driver ODBC de Microsoft para SQL Server.
# Los drivers de PostgreSQL (asyncpg) y MariaDB (aiomysql) son
# librerias de Python puras y no necesitan nada extra, pero
# SQL Server se conecta via ODBC y ese driver es del sistema
# operativo, por eso se instala con apt-get y no con pip.
# --------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends curl gnupg2 ca-certificates \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 unixodbc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar las dependencias de Python primero (se cachean si no cambian)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el codigo de la aplicacion
COPY . .

# Comando por defecto (docker-compose.yml lo sobreescribe para desarrollo)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8011"]
