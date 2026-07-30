# ==============================================================
# Dockerfile del Frontend (Flask)
#
# El front NO se conecta a las bases de datos: solo hace
# peticiones HTTP a las APIs. Por eso su imagen es muy simple.
# ==============================================================
FROM python:3.12-slim

WORKDIR /app

# Instalar las dependencias primero (se cachean si no cambian)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el codigo de la aplicacion
COPY . .

# Comando por defecto (docker-compose.yml lo sobreescribe para desarrollo)
CMD ["flask", "--app", "app", "run", "--host", "0.0.0.0", "--port", "8000"]
