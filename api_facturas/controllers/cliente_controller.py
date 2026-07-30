"""
cliente_controller.py — Controller específico para la tabla cliente.

Endpoints:
- GET    /api/cliente/          → Listar clientes
- GET    /api/cliente/{id}      → Obtener cliente por id
- POST   /api/cliente/          → Crear cliente
- PUT    /api/cliente/{id}      → Actualizar cliente
- DELETE /api/cliente/{id}      → Eliminar cliente
"""

from fastapi import APIRouter, HTTPException, Query, Response

from models.cliente import Cliente
from servicios.fabrica_repositorios import crear_servicio_cliente


router = APIRouter(prefix="/api/cliente", tags=["Cliente"])


# =========================================================================
# GET /api/cliente/ — Listar todos los clientes
# =========================================================================

@router.get("/")
async def listar_clientes(
    esquema: str | None = Query(default=None),
    limite: int | None = Query(default=None)
):
    """Lista todos los clientes."""
    try:
        servicio = crear_servicio_cliente()
        filas = await servicio.listar(esquema, limite)

        if len(filas) == 0:
            return Response(status_code=204)

        return {
            "tabla": "cliente",
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
# GET /api/cliente/{id} — Obtener cliente por id
# =========================================================================

@router.get("/{id}")
async def obtener_cliente(
    id: int,
    esquema: str | None = Query(default=None)
):
    """Obtiene un cliente por su id."""
    try:
        servicio = crear_servicio_cliente()
        filas = await servicio.obtener_por_id(id, esquema)

        if len(filas) == 0:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No se encontró cliente con id = {id}"
            })

        return {
            "tabla": "cliente",
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
# POST /api/cliente/ — Crear cliente
# =========================================================================

@router.post("/")
async def crear_cliente(
    cliente: Cliente,
    esquema: str | None = Query(default=None)
):
    """Crea un nuevo cliente. Valida con el modelo Pydantic."""
    try:
        datos = cliente.model_dump(exclude_none=True)
        servicio = crear_servicio_cliente()
        creado = await servicio.crear(datos, esquema)

        if creado:
            return {
                "estado": 200,
                "mensaje": "Cliente creado exitosamente.",
                "datos": datos
            }
        else:
            raise HTTPException(status_code=500, detail={
                "estado": 500, "mensaje": "No se pudo crear el cliente."
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
# PUT /api/cliente/{id} — Actualizar cliente
# =========================================================================

@router.put("/{id}")
async def actualizar_cliente(
    id: int,
    cliente: Cliente,
    esquema: str | None = Query(default=None)
):
    """Actualiza un cliente existente."""
    try:
        datos = cliente.model_dump(exclude={"id"}, exclude_none=True)
        servicio = crear_servicio_cliente()
        filas = await servicio.actualizar(id, datos, esquema)

        if filas > 0:
            return {
                "estado": 200,
                "mensaje": "Cliente actualizado exitosamente.",
                "filtro": f"id = {id}",
                "filasAfectadas": filas
            }
        else:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No existe cliente con id = {id}"
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
# DELETE /api/cliente/{id} — Eliminar cliente
# =========================================================================

@router.delete("/{id}")
async def eliminar_cliente(
    id: int,
    esquema: str | None = Query(default=None)
):
    """Elimina un cliente por su id."""
    try:
        servicio = crear_servicio_cliente()
        filas = await servicio.eliminar(id, esquema)

        if filas > 0:
            return {
                "estado": 200,
                "mensaje": "Cliente eliminado exitosamente.",
                "filtro": f"id = {id}",
                "filasEliminadas": filas
            }
        else:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No existe cliente con id = {id}"
            })

    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })
