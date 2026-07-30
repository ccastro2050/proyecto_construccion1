"""
vendedor_controller.py — Controller específico para la tabla vendedor.

Endpoints:
- GET    /api/vendedor/          → Listar vendedores
- GET    /api/vendedor/{id}      → Obtener vendedor por id
- POST   /api/vendedor/          → Crear vendedor
- PUT    /api/vendedor/{id}      → Actualizar vendedor
- DELETE /api/vendedor/{id}      → Eliminar vendedor
"""

from fastapi import APIRouter, HTTPException, Query, Response

from models.vendedor import Vendedor
from servicios.fabrica_repositorios import crear_servicio_vendedor


router = APIRouter(prefix="/api/vendedor", tags=["Vendedor"])


# =========================================================================
# GET /api/vendedor/ — Listar todos los vendedores
# =========================================================================

@router.get("/")
async def listar_vendedores(
    esquema: str | None = Query(default=None),
    limite: int | None = Query(default=None)
):
    """Lista todos los vendedores."""
    try:
        servicio = crear_servicio_vendedor()
        filas = await servicio.listar(esquema, limite)

        if len(filas) == 0:
            return Response(status_code=204)

        return {
            "tabla": "vendedor",
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
# GET /api/vendedor/{id} — Obtener vendedor por id
# =========================================================================

@router.get("/{id}")
async def obtener_vendedor(
    id: int,
    esquema: str | None = Query(default=None)
):
    """Obtiene un vendedor por su id."""
    try:
        servicio = crear_servicio_vendedor()
        filas = await servicio.obtener_por_id(id, esquema)

        if len(filas) == 0:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No se encontró vendedor con id = {id}"
            })

        return {
            "tabla": "vendedor",
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
# POST /api/vendedor/ — Crear vendedor
# =========================================================================

@router.post("/")
async def crear_vendedor(
    vendedor: Vendedor,
    esquema: str | None = Query(default=None)
):
    """Crea un nuevo vendedor. Valida con el modelo Pydantic."""
    try:
        datos = vendedor.model_dump(exclude_none=True)
        servicio = crear_servicio_vendedor()
        creado = await servicio.crear(datos, esquema)

        if creado:
            return {
                "estado": 200,
                "mensaje": "Vendedor creado exitosamente.",
                "datos": datos
            }
        else:
            raise HTTPException(status_code=500, detail={
                "estado": 500, "mensaje": "No se pudo crear el vendedor."
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
# PUT /api/vendedor/{id} — Actualizar vendedor
# =========================================================================

@router.put("/{id}")
async def actualizar_vendedor(
    id: int,
    vendedor: Vendedor,
    esquema: str | None = Query(default=None)
):
    """Actualiza un vendedor existente."""
    try:
        datos = vendedor.model_dump(exclude={"id"}, exclude_none=True)
        servicio = crear_servicio_vendedor()
        filas = await servicio.actualizar(id, datos, esquema)

        if filas > 0:
            return {
                "estado": 200,
                "mensaje": "Vendedor actualizado exitosamente.",
                "filtro": f"id = {id}",
                "filasAfectadas": filas
            }
        else:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No existe vendedor con id = {id}"
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
# DELETE /api/vendedor/{id} — Eliminar vendedor
# =========================================================================

@router.delete("/{id}")
async def eliminar_vendedor(
    id: int,
    esquema: str | None = Query(default=None)
):
    """Elimina un vendedor por su id."""
    try:
        servicio = crear_servicio_vendedor()
        filas = await servicio.eliminar(id, esquema)

        if filas > 0:
            return {
                "estado": 200,
                "mensaje": "Vendedor eliminado exitosamente.",
                "filtro": f"id = {id}",
                "filasEliminadas": filas
            }
        else:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No existe vendedor con id = {id}"
            })

    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })
