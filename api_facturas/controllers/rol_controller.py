"""
rol_controller.py — Controller específico para la tabla rol.

Endpoints:
- GET    /api/rol/          → Listar roles
- GET    /api/rol/{id}      → Obtener rol por id
- POST   /api/rol/          → Crear rol
- PUT    /api/rol/{id}      → Actualizar rol
- DELETE /api/rol/{id}      → Eliminar rol
"""

from fastapi import APIRouter, HTTPException, Query, Response

from models.rol import Rol
from servicios.fabrica_repositorios import crear_servicio_rol


router = APIRouter(prefix="/api/rol", tags=["Rol"])


# =========================================================================
# GET /api/rol/ — Listar todos los roles
# =========================================================================

@router.get("/")
async def listar_roles(
    esquema: str | None = Query(default=None),
    limite: int | None = Query(default=None)
):
    """Lista todos los roles."""
    try:
        servicio = crear_servicio_rol()
        filas = await servicio.listar(esquema, limite)

        if len(filas) == 0:
            return Response(status_code=204)

        return {
            "tabla": "rol",
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
# GET /api/rol/{id} — Obtener rol por id
# =========================================================================

@router.get("/{id}")
async def obtener_rol(
    id: int,
    esquema: str | None = Query(default=None)
):
    """Obtiene un rol por su id."""
    try:
        servicio = crear_servicio_rol()
        filas = await servicio.obtener_por_id(id, esquema)

        if len(filas) == 0:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No se encontró rol con id = {id}"
            })

        return {
            "tabla": "rol",
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
# POST /api/rol/ — Crear rol
# =========================================================================

@router.post("/")
async def crear_rol(
    rol: Rol,
    esquema: str | None = Query(default=None)
):
    """Crea un nuevo rol. Valida con el modelo Pydantic."""
    try:
        datos = rol.model_dump(exclude_none=True)
        servicio = crear_servicio_rol()
        creado = await servicio.crear(datos, esquema)

        if creado:
            return {
                "estado": 200,
                "mensaje": "Rol creado exitosamente.",
                "datos": datos
            }
        else:
            raise HTTPException(status_code=500, detail={
                "estado": 500, "mensaje": "No se pudo crear el rol."
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
# PUT /api/rol/{id} — Actualizar rol
# =========================================================================

@router.put("/{id}")
async def actualizar_rol(
    id: int,
    rol: Rol,
    esquema: str | None = Query(default=None)
):
    """Actualiza un rol existente."""
    try:
        datos = rol.model_dump(exclude={"id"})
        servicio = crear_servicio_rol()
        filas = await servicio.actualizar(id, datos, esquema)

        if filas > 0:
            return {
                "estado": 200,
                "mensaje": "Rol actualizado exitosamente.",
                "filtro": f"id = {id}",
                "filasAfectadas": filas
            }
        else:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No existe rol con id = {id}"
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
# DELETE /api/rol/{id} — Eliminar rol
# =========================================================================

@router.delete("/{id}")
async def eliminar_rol(
    id: int,
    esquema: str | None = Query(default=None)
):
    """Elimina un rol por su id."""
    try:
        servicio = crear_servicio_rol()
        filas = await servicio.eliminar(id, esquema)

        if filas > 0:
            return {
                "estado": 200,
                "mensaje": "Rol eliminado exitosamente.",
                "filtro": f"id = {id}",
                "filasEliminadas": filas
            }
        else:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No existe rol con id = {id}"
            })

    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })
