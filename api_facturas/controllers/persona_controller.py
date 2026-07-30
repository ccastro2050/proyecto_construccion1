"""
persona_controller.py — Controller específico para la tabla persona.

A diferencia del controlador genérico (entidades_controller),
este usa el modelo Pydantic Persona para validación estricta.

Endpoints:
- GET    /api/persona/              → Listar personas
- GET    /api/persona/{codigo}      → Obtener persona por código
- POST   /api/persona/              → Crear persona
- PUT    /api/persona/{codigo}      → Actualizar persona
- DELETE /api/persona/{codigo}      → Eliminar persona
"""

from fastapi import APIRouter, HTTPException, Query, Response

from models.persona import Persona
from servicios.fabrica_repositorios import crear_servicio_persona


router = APIRouter(prefix="/api/persona", tags=["Persona"])


# =========================================================================
# GET /api/persona/ — Listar todas las personas
# =========================================================================

@router.get("/")
async def listar_personas(
    esquema: str | None = Query(default=None),
    limite: int | None = Query(default=None)
):
    """Lista todas las personas."""
    try:
        servicio = crear_servicio_persona()
        filas = await servicio.listar(esquema, limite)

        if len(filas) == 0:
            return Response(status_code=204)

        return {
            "tabla": "persona",
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
# GET /api/persona/{codigo} — Obtener persona por código
# =========================================================================

@router.get("/{codigo}")
async def obtener_persona(
    codigo: str,
    esquema: str | None = Query(default=None)
):
    """Obtiene una persona por su código."""
    try:
        servicio = crear_servicio_persona()
        filas = await servicio.obtener_por_codigo(codigo, esquema)

        if len(filas) == 0:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No se encontró persona con codigo = {codigo}"
            })

        return {
            "tabla": "persona",
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
# POST /api/persona/ — Crear persona
# =========================================================================

@router.post("/")
async def crear_persona(
    persona: Persona,
    esquema: str | None = Query(default=None)
):
    """Crea una nueva persona. Valida con el modelo Pydantic."""
    try:
        datos = persona.model_dump()
        servicio = crear_servicio_persona()
        creado = await servicio.crear(datos, esquema)

        if creado:
            return {
                "estado": 200,
                "mensaje": "Persona creada exitosamente.",
                "datos": datos
            }
        else:
            raise HTTPException(status_code=500, detail={
                "estado": 500, "mensaje": "No se pudo crear la persona."
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
# PUT /api/persona/{codigo} — Actualizar persona
# =========================================================================

@router.put("/{codigo}")
async def actualizar_persona(
    codigo: str,
    persona: Persona,
    esquema: str | None = Query(default=None)
):
    """Actualiza una persona existente."""
    try:
        datos = persona.model_dump(exclude={"codigo"})
        servicio = crear_servicio_persona()
        filas = await servicio.actualizar(codigo, datos, esquema)

        if filas > 0:
            return {
                "estado": 200,
                "mensaje": "Persona actualizada exitosamente.",
                "filtro": f"codigo = {codigo}",
                "filasAfectadas": filas
            }
        else:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No existe persona con codigo = {codigo}"
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
# DELETE /api/persona/{codigo} — Eliminar persona
# =========================================================================

@router.delete("/{codigo}")
async def eliminar_persona(
    codigo: str,
    esquema: str | None = Query(default=None)
):
    """Elimina una persona por su código."""
    try:
        servicio = crear_servicio_persona()
        filas = await servicio.eliminar(codigo, esquema)

        if filas > 0:
            return {
                "estado": 200,
                "mensaje": "Persona eliminada exitosamente.",
                "filtro": f"codigo = {codigo}",
                "filasEliminadas": filas
            }
        else:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No existe persona con codigo = {codigo}"
            })

    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })
