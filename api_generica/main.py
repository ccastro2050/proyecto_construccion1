"""
main.py — Punto de entrada de la API CRUD genérica.

Configura la aplicación FastAPI:
1. Crea la app con documentación Swagger automática
2. Configura CORS (para que frontends puedan consumir la API)
3. Registra el controlador de entidades (CRUD)
4. Arranca el servidor con uvicorn

Ejecución:
  python main.py                              (desarrollo con auto-reload)
  uvicorn main:app --host 0.0.0.0 --port 8000  (producción)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from controllers import entidades_controller

# Cargar configuración desde .env
settings = get_settings()

# ================================================================
# CREAR APLICACIÓN
# ================================================================

app = FastAPI(
    title="API Genérica CRUD",
    description="API REST genérica para operaciones CRUD sobre cualquier tabla. "
                "Soporta SQL Server, PostgreSQL y MySQL/MariaDB.",
    version="1.0.0",
    docs_url="/swagger",
    redoc_url="/redoc",
    openapi_url="/swagger/v1/swagger.json",
)

# ================================================================
# CORS — Permite que frontends en otros puertos consuman la API
# ================================================================
# Sin esto, un frontend en localhost:3000 no puede llamar a localhost:8000
# porque el navegador bloquea la petición por seguridad (Same-Origin Policy).

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Cualquier origen puede consumir la API
    allow_credentials=True,
    allow_methods=["*"],       # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],       # Cualquier header
)

# ================================================================
# REGISTRAR CONTROLADORES
# ================================================================
# Cada controlador es un "Router" que agrupa endpoints relacionados.
# include_router() los conecta a la aplicación.

app.include_router(entidades_controller)

# ================================================================
# ENDPOINT RAÍZ — Verificar que la API funciona
# ================================================================

@app.get("/", tags=["Diagnóstico"])
async def root():
    """Retorna un mensaje básico para verificar que la API está activa."""
    return {
        "mensaje": "API CRUD genérica funcionando",
        "version": "1.0.0",
        "entorno": settings.environment,
        "documentacion": {
            "swagger": "/swagger",
            "redoc": "/redoc"
        }
    }

# ================================================================
# EJECUCIÓN DIRECTA (solo para desarrollo)
# ================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )
