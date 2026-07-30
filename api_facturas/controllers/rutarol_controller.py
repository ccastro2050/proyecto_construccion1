"""
rutarol_controller.py — Controller para la tabla rutarol.

Tabla de relación ruta-rol con PK compuesta (ruta, rol).

Endpoints:
- GET    /api/rutarol/                  → Listar relaciones
- GET    /api/rutarol/rol/{rol}          → Rutas de un rol
- POST   /api/rutarol/                  → Crear relación
- DELETE /api/rutarol/{ruta}/{rol}      → Eliminar relación
"""

from fastapi import APIRouter, HTTPException, Query, Response

from models.rutarol import RutaRol
from servicios.fabrica_repositorios import crear_servicio_rutarol


router = APIRouter(prefix="/api/rutarol", tags=["RutaRol"])


# =========================================================================
# GET /api/rutarol/ — Listar todas las relaciones
# =========================================================================

@router.get("/")
async def listar_rutarol(
    esquema: str | None = Query(default=None),
    limite: int | None = Query(default=None)
):
    """Lista todas las relaciones ruta-rol."""
    try:
        servicio = crear_servicio_rutarol()
        filas = await servicio.listar(esquema, limite)

        if len(filas) == 0:
            return Response(status_code=204)

        return {
            "tabla": "rutarol",
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
# GET /api/rutarol/rol/{rol} — Rutas de un rol
# =========================================================================

@router.get("/rol/{rol}")
async def obtener_rutas_de_rol(
    rol: str,
    esquema: str | None = Query(default=None)
):
    """Obtiene las rutas asignadas a un rol."""
    try:
        servicio = crear_servicio_rutarol()
        filas = await servicio.obtener_por_rol(rol, esquema)

        if len(filas) == 0:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No se encontraron rutas para el rol {rol}"
            })

        return {
            "tabla": "rutarol",
            "filtro": f"rol = {rol}",
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
# POST /api/rutarol/ — Crear relación
# =========================================================================

@router.post("/")
async def crear_rutarol(
    rutarol: RutaRol,
    esquema: str | None = Query(default=None)
):
    """Asigna una ruta a un rol."""
    try:
        datos = rutarol.model_dump()
        servicio = crear_servicio_rutarol()
        creado = await servicio.crear(datos, esquema)

        if creado:
            return {
                "estado": 200,
                "mensaje": "Ruta asignada al rol exitosamente.",
                "datos": datos
            }
        else:
            raise HTTPException(status_code=500, detail={
                "estado": 500, "mensaje": "No se pudo asignar la ruta."
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
# DELETE /api/rutarol/{ruta}/{rol} — Eliminar relación
# =========================================================================

@router.delete("/{valor_ruta}/{rol}")
async def eliminar_rutarol(
    valor_ruta: str,
    rol: str,
    esquema: str | None = Query(default=None)
):
    """Quita una ruta de un rol."""
    try:
        servicio = crear_servicio_rutarol()
        filas = await servicio.eliminar(valor_ruta, esquema)

        if filas > 0:
            return {
                "estado": 200,
                "mensaje": "Ruta removida del rol exitosamente.",
                "filtro": f"ruta = {valor_ruta}, rol = {rol}",
                "filasEliminadas": filas
            }
        else:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No existe relación ruta = {valor_ruta}, rol = {rol}"
            })

    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })
