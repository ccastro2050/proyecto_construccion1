"""
rol_usuario_controller.py — Controller para la tabla rol_usuario.

Tabla de relación muchos-a-muchos con PK compuesta (fkemail, fkidrol).

Endpoints:
- GET    /api/rol-usuario/                      → Listar relaciones
- GET    /api/rol-usuario/usuario/{fkemail}      → Roles de un usuario
- GET    /api/rol-usuario/rol/{fkidrol}          → Usuarios de un rol
- POST   /api/rol-usuario/                      → Crear relación
- DELETE /api/rol-usuario/{fkemail}/{fkidrol}    → Eliminar relación
"""

from fastapi import APIRouter, HTTPException, Query, Response

from models.rol_usuario import RolUsuario
from servicios.fabrica_repositorios import crear_servicio_rol_usuario


router = APIRouter(prefix="/api/rol-usuario", tags=["RolUsuario"])


# =========================================================================
# GET /api/rol-usuario/ — Listar todas las relaciones
# =========================================================================

@router.get("/")
async def listar_roles_usuarios(
    esquema: str | None = Query(default=None),
    limite: int | None = Query(default=None)
):
    """Lista todas las relaciones rol-usuario."""
    try:
        servicio = crear_servicio_rol_usuario()
        filas = await servicio.listar(esquema, limite)

        if len(filas) == 0:
            return Response(status_code=204)

        return {
            "tabla": "rol_usuario",
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
# GET /api/rol-usuario/usuario/{fkemail} — Roles de un usuario
# =========================================================================

@router.get("/usuario/{fkemail}")
async def obtener_roles_de_usuario(
    fkemail: str,
    esquema: str | None = Query(default=None)
):
    """Obtiene los roles asignados a un usuario."""
    try:
        servicio = crear_servicio_rol_usuario()
        filas = await servicio.obtener_por_email(fkemail, esquema)

        if len(filas) == 0:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No se encontraron roles para el usuario {fkemail}"
            })

        return {
            "tabla": "rol_usuario",
            "filtro": f"fkemail = {fkemail}",
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
# GET /api/rol-usuario/rol/{fkidrol} — Usuarios de un rol
# =========================================================================

@router.get("/rol/{fkidrol}")
async def obtener_usuarios_de_rol(
    fkidrol: int,
    esquema: str | None = Query(default=None)
):
    """Obtiene los usuarios que tienen un rol específico."""
    try:
        servicio = crear_servicio_rol_usuario()
        filas = await servicio.obtener_por_rol(fkidrol, esquema)

        if len(filas) == 0:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No se encontraron usuarios para el rol {fkidrol}"
            })

        return {
            "tabla": "rol_usuario",
            "filtro": f"fkidrol = {fkidrol}",
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
# POST /api/rol-usuario/ — Crear relación
# =========================================================================

@router.post("/")
async def crear_rol_usuario(
    rol_usuario: RolUsuario,
    esquema: str | None = Query(default=None)
):
    """Asigna un rol a un usuario."""
    try:
        datos = rol_usuario.model_dump()
        servicio = crear_servicio_rol_usuario()
        creado = await servicio.crear(datos, esquema)

        if creado:
            return {
                "estado": 200,
                "mensaje": "Rol asignado al usuario exitosamente.",
                "datos": datos
            }
        else:
            raise HTTPException(status_code=500, detail={
                "estado": 500, "mensaje": "No se pudo asignar el rol."
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
# DELETE /api/rol-usuario/{fkemail}/{fkidrol} — Eliminar relación
# =========================================================================

@router.delete("/{fkemail}/{fkidrol}")
async def eliminar_rol_usuario(
    fkemail: str,
    fkidrol: int,
    esquema: str | None = Query(default=None)
):
    """Quita un rol de un usuario."""
    try:
        servicio = crear_servicio_rol_usuario()
        filas = await servicio.eliminar(fkemail, esquema)

        if filas > 0:
            return {
                "estado": 200,
                "mensaje": "Rol removido del usuario exitosamente.",
                "filtro": f"fkemail = {fkemail}, fkidrol = {fkidrol}",
                "filasEliminadas": filas
            }
        else:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No existe relación fkemail = {fkemail}, fkidrol = {fkidrol}"
            })

    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })
