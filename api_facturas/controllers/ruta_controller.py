"""
ruta_controller.py — Controller específico para la tabla ruta.

Endpoints:
- GET    /api/ruta/              → Listar rutas
- GET    /api/ruta/{ruta}        → Obtener ruta por su valor
- POST   /api/ruta/              → Crear ruta
- PUT    /api/ruta/{ruta}        → Actualizar ruta
- DELETE /api/ruta/{ruta}        → Eliminar ruta
"""

from fastapi import APIRouter, HTTPException, Query, Response

from models.ruta import Ruta
from servicios.fabrica_repositorios import crear_servicio_ruta


router = APIRouter(prefix="/api/ruta", tags=["Ruta"])


# =========================================================================
# GET /api/ruta/ — Listar todas las rutas
# =========================================================================

@router.get("/")
async def listar_rutas(
    esquema: str | None = Query(default=None),
    limite: int | None = Query(default=None)
):
    """Lista todas las rutas."""
    try:
        servicio = crear_servicio_ruta()
        filas = await servicio.listar(esquema, limite)

        if len(filas) == 0:
            return Response(status_code=204)

        return {
            "tabla": "ruta",
            "total": len(filas),
            "datos": filas
        }

    except ValueError as ex:
        raise HTTPException(status_code=400, detail={
            "estado": 400, "mensaje": "Parámetros inválidos.", "detalle": str(ex)
        })
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })


# =========================================================================
# GET /api/ruta/{valor_ruta} — Obtener ruta por su valor
# =========================================================================

@router.get("/{valor_ruta:path}")
async def obtener_ruta(
    valor_ruta: str,
    esquema: str | None = Query(default=None)
):
    """Obtiene una ruta por su valor."""
    try:
        servicio = crear_servicio_ruta()
        filas = await servicio.obtener_por_ruta(valor_ruta, esquema)

        if len(filas) == 0:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No se encontró ruta = {valor_ruta}"
            })

        return {
            "tabla": "ruta",
            "total": len(filas),
            "datos": filas
        }

    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })


# =========================================================================
# POST /api/ruta/ — Crear ruta
# =========================================================================

@router.post("/")
async def crear_ruta(
    ruta: Ruta,
    esquema: str | None = Query(default=None)
):
    """Crea una nueva ruta. Valida con el modelo Pydantic."""
    try:
        datos = ruta.model_dump()
        servicio = crear_servicio_ruta()
        creado = await servicio.crear(datos, esquema)

        if creado:
            return {
                "estado": 200,
                "mensaje": "Ruta creada exitosamente.",
                "datos": datos
            }
        else:
            raise HTTPException(status_code=500, detail={
                "estado": 500, "mensaje": "No se pudo crear la ruta."
            })

    except HTTPException:
        raise
    except ValueError as ex:
        raise HTTPException(status_code=400, detail={
            "estado": 400, "mensaje": "Datos inválidos.", "detalle": str(ex)
        })
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })


# =========================================================================
# PUT /api/ruta/{valor_ruta} — Actualizar ruta
# =========================================================================

@router.put("/{valor_ruta:path}")
async def actualizar_ruta(
    valor_ruta: str,
    ruta: Ruta,
    esquema: str | None = Query(default=None)
):
    """Actualiza una ruta existente."""
    try:
        datos = ruta.model_dump(exclude={"ruta"})
        servicio = crear_servicio_ruta()
        filas = await servicio.actualizar(valor_ruta, datos, esquema)

        if filas > 0:
            return {
                "estado": 200,
                "mensaje": "Ruta actualizada exitosamente.",
                "filtro": f"ruta = {valor_ruta}",
                "filasAfectadas": filas
            }
        else:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No existe ruta = {valor_ruta}"
            })

    except HTTPException:
        raise
    except ValueError as ex:
        raise HTTPException(status_code=400, detail={
            "estado": 400, "mensaje": "Datos inválidos.", "detalle": str(ex)
        })
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })


# =========================================================================
# DELETE /api/ruta/{valor_ruta} — Eliminar ruta
# =========================================================================

@router.delete("/{valor_ruta:path}")
async def eliminar_ruta(
    valor_ruta: str,
    esquema: str | None = Query(default=None)
):
    """Elimina una ruta por su valor."""
    try:
        servicio = crear_servicio_ruta()
        filas = await servicio.eliminar(valor_ruta, esquema)

        if filas > 0:
            return {
                "estado": 200,
                "mensaje": "Ruta eliminada exitosamente.",
                "filtro": f"ruta = {valor_ruta}",
                "filasEliminadas": filas
            }
        else:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No existe ruta = {valor_ruta}"
            })

    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })
