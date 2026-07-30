"""
empresa_controller.py — Controller específico para la tabla empresa.

Endpoints:
- GET    /api/empresa/              → Listar empresas
- GET    /api/empresa/{codigo}      → Obtener empresa por código
- POST   /api/empresa/              → Crear empresa
- PUT    /api/empresa/{codigo}      → Actualizar empresa
- DELETE /api/empresa/{codigo}      → Eliminar empresa
"""

from fastapi import APIRouter, HTTPException, Query, Response

from models.empresa import Empresa
from servicios.fabrica_repositorios import crear_servicio_empresa


router = APIRouter(prefix="/api/empresa", tags=["Empresa"])


# =========================================================================
# GET /api/empresa/ — Listar todas las empresas
# =========================================================================

@router.get("/")
async def listar_empresas(
    esquema: str | None = Query(default=None),
    limite: int | None = Query(default=None)
):
    """Lista todas las empresas."""
    try:
        servicio = crear_servicio_empresa()
        filas = await servicio.listar(esquema, limite)

        if len(filas) == 0:
            return Response(status_code=204)

        return {
            "tabla": "empresa",
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
# GET /api/empresa/{codigo} — Obtener empresa por código
# =========================================================================

@router.get("/{codigo}")
async def obtener_empresa(
    codigo: str,
    esquema: str | None = Query(default=None)
):
    """Obtiene una empresa por su código."""
    try:
        servicio = crear_servicio_empresa()
        filas = await servicio.obtener_por_codigo(codigo, esquema)

        if len(filas) == 0:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No se encontró empresa con codigo = {codigo}"
            })

        return {
            "tabla": "empresa",
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
# POST /api/empresa/ — Crear empresa
# =========================================================================

@router.post("/")
async def crear_empresa(
    empresa: Empresa,
    esquema: str | None = Query(default=None)
):
    """Crea una nueva empresa. Valida con el modelo Pydantic."""
    try:
        datos = empresa.model_dump()
        servicio = crear_servicio_empresa()
        creado = await servicio.crear(datos, esquema)

        if creado:
            return {
                "estado": 200,
                "mensaje": "Empresa creada exitosamente.",
                "datos": datos
            }
        else:
            raise HTTPException(status_code=500, detail={
                "estado": 500, "mensaje": "No se pudo crear la empresa."
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
# PUT /api/empresa/{codigo} — Actualizar empresa
# =========================================================================

@router.put("/{codigo}")
async def actualizar_empresa(
    codigo: str,
    empresa: Empresa,
    esquema: str | None = Query(default=None)
):
    """Actualiza una empresa existente."""
    try:
        datos = empresa.model_dump(exclude={"codigo"})
        servicio = crear_servicio_empresa()
        filas = await servicio.actualizar(codigo, datos, esquema)

        if filas > 0:
            return {
                "estado": 200,
                "mensaje": "Empresa actualizada exitosamente.",
                "filtro": f"codigo = {codigo}",
                "filasAfectadas": filas
            }
        else:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No existe empresa con codigo = {codigo}"
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
# DELETE /api/empresa/{codigo} — Eliminar empresa
# =========================================================================

@router.delete("/{codigo}")
async def eliminar_empresa(
    codigo: str,
    esquema: str | None = Query(default=None)
):
    """Elimina una empresa por su código."""
    try:
        servicio = crear_servicio_empresa()
        filas = await servicio.eliminar(codigo, esquema)

        if filas > 0:
            return {
                "estado": 200,
                "mensaje": "Empresa eliminada exitosamente.",
                "filtro": f"codigo = {codigo}",
                "filasEliminadas": filas
            }
        else:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No existe empresa con codigo = {codigo}"
            })

    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })
