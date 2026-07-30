"""
config.py — Configuración del frontend.

Aquí se definen las URL de las dos APIs que el front puede consumir.
Se leen de variables de entorno (las pone docker-compose.yml); si no
existen, se usan valores por defecto que sirven para correr el front
fuera de Docker.

CONCEPTO — Variables de entorno:
    Son valores que "viven" fuera del código. Así el mismo código
    funciona en Docker (donde la API se llama http://api-generica:8001)
    y en su PC (donde sería http://localhost:8001) sin cambiar nada.
"""
import os

# URL de la API Genérica (CRUD sobre cualquier tabla)
API_GENERICA_URL = os.getenv("API_GENERICA_URL", "http://localhost:8001")

# URL de la API de Facturas (CRUD por entidad, con validación Pydantic)
API_FACTURAS_URL = os.getenv("API_FACTURAS_URL", "http://localhost:8002")

# Clave con la que Flask firma la sesión (guarda qué API eligió el usuario).
# En un proyecto real esta clave debe ser secreta y venir del entorno.
SECRET_KEY = os.getenv("SECRET_KEY", "clave-de-desarrollo-paradigmas")
