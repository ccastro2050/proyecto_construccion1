"""
main.py — Punto de entrada de la API REST con FastAPI.

Registra los routers (controladores) y arranca la aplicación.
Ejecutar con: uvicorn main:app --reload
"""

from fastapi import FastAPI

from controllers.persona_controller import router as persona_router
from controllers.empresa_controller import router as empresa_router
from controllers.cliente_controller import router as cliente_router
from controllers.vendedor_controller import router as vendedor_router
from controllers.producto_controller import router as producto_router
from controllers.factura_controller import router as factura_router
from controllers.productosporfactura_controller import router as detalle_router
from controllers.usuario_controller import router as usuario_router
from controllers.rol_controller import router as rol_router
from controllers.rol_usuario_controller import router as rol_usuario_router
from controllers.ruta_controller import router as ruta_router
from controllers.rutarol_controller import router as rutarol_router
from controllers.entidades_controller import router as entidades_router


app = FastAPI(
    title="API Facturas CRUD",
    description="API REST genérica para operaciones CRUD sobre la base de datos de facturas.",
    version="1.0.0",
)

# ── Registrar controladores ──────────────────────────────────────────
# Los controllers específicos van primero para que sus rutas
# tengan prioridad sobre las genéricas de entidades_controller (/api/{tabla}).

app.include_router(persona_router)
app.include_router(empresa_router)
app.include_router(cliente_router)
app.include_router(vendedor_router)
app.include_router(producto_router)
app.include_router(factura_router)
app.include_router(detalle_router)
app.include_router(usuario_router)
app.include_router(rol_router)
app.include_router(rol_usuario_router)
app.include_router(ruta_router)
app.include_router(rutarol_router)

# El controller genérico va de último (atrapa /api/{tabla} restante)
app.include_router(entidades_router)


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raíz de verificación."""
    return {
        "mensaje": "API Facturas CRUD activa.",
        "docs": "/docs",
        "redoc": "/redoc"
    }
