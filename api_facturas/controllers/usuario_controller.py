"""
usuario_controller.py — Controller específico para la tabla usuario.

Endpoints:
- GET    /api/usuario/                      → Listar usuarios
- GET    /api/usuario/{email}               → Obtener usuario por email
- POST   /api/usuario/                      → Crear usuario (encripta contraseña)
- PUT    /api/usuario/{email}               → Actualizar usuario
- DELETE /api/usuario/{email}               → Eliminar usuario
- POST   /api/usuario/verificar-contrasena  → Verificar credenciales
"""

from fastapi import APIRouter, HTTPException, Query, Response

from models.usuario import Usuario
from servicios.fabrica_repositorios import crear_servicio_usuario


router = APIRouter(prefix="/api/usuario", tags=["Usuario"])


# =========================================================================
# GET /api/usuario/ — Listar todos los usuarios
# =========================================================================

@router.get("/")
async def listar_usuarios(
    esquema: str | None = Query(default=None),
    limite: int | None = Query(default=None)
):
    """Lista todos los usuarios."""
    try:
        servicio = crear_servicio_usuario()
        filas = await servicio.listar(esquema, limite)

        if len(filas) == 0:
            return Response(status_code=204)

        return {
            "tabla": "usuario",
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
# GET /api/usuario/{email} — Obtener usuario por email
# =========================================================================

@router.get("/{email}")
async def obtener_usuario(
    email: str,
    esquema: str | None = Query(default=None)
):
    """Obtiene un usuario por su email."""
    try:
        servicio = crear_servicio_usuario()
        filas = await servicio.obtener_por_email(email, esquema)

        if len(filas) == 0:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No se encontró usuario con email = {email}"
            })

        return {
            "tabla": "usuario",
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
# POST /api/usuario/ — Crear usuario (encripta contraseña con BCrypt)
# =========================================================================

@router.post("/")
async def crear_usuario(
    usuario: Usuario,
    esquema: str | None = Query(default=None)
):
    """Crea un nuevo usuario. La contraseña se encripta con BCrypt."""
    try:
        datos = usuario.model_dump()
        servicio = crear_servicio_usuario()
        creado = await servicio.crear(datos, esquema)

        if creado:
            return {
                "estado": 200,
                "mensaje": "Usuario creado exitosamente.",
                "email": usuario.email
            }
        else:
            raise HTTPException(status_code=500, detail={
                "estado": 500, "mensaje": "No se pudo crear el usuario."
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
# PUT /api/usuario/{email} — Actualizar usuario
# =========================================================================

@router.put("/{email}")
async def actualizar_usuario(
    email: str,
    usuario: Usuario,
    esquema: str | None = Query(default=None)
):
    """Actualiza un usuario existente. La contraseña se re-encripta."""
    try:
        datos = usuario.model_dump(exclude={"email"})
        servicio = crear_servicio_usuario()
        filas = await servicio.actualizar(email, datos, esquema)

        if filas > 0:
            return {
                "estado": 200,
                "mensaje": "Usuario actualizado exitosamente.",
                "filtro": f"email = {email}",
                "filasAfectadas": filas
            }
        else:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No existe usuario con email = {email}"
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
# DELETE /api/usuario/{email} — Eliminar usuario
# =========================================================================

@router.delete("/{email}")
async def eliminar_usuario(
    email: str,
    esquema: str | None = Query(default=None)
):
    """Elimina un usuario por su email."""
    try:
        servicio = crear_servicio_usuario()
        filas = await servicio.eliminar(email, esquema)

        if filas > 0:
            return {
                "estado": 200,
                "mensaje": "Usuario eliminado exitosamente.",
                "filtro": f"email = {email}",
                "filasEliminadas": filas
            }
        else:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No existe usuario con email = {email}"
            })

    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })


# =========================================================================
# POST /api/usuario/verificar-contrasena — Verificar credenciales
# =========================================================================

@router.post("/verificar-contrasena")
async def verificar_contrasena(
    valor_usuario: str = Query(..., description="Email del usuario"),
    valor_contrasena: str = Query(..., description="Contraseña a verificar"),
    esquema: str | None = Query(default=None)
):
    """Verifica credenciales de un usuario contra la BD usando BCrypt."""
    try:
        servicio = crear_servicio_usuario()
        codigo, mensaje = await servicio.verificar_contrasena(
            valor_usuario, valor_contrasena, esquema
        )

        if codigo == 200:
            return {"estado": 200, "mensaje": mensaje, "usuario": valor_usuario}
        elif codigo == 404:
            raise HTTPException(status_code=404, detail={
                "estado": 404, "mensaje": mensaje, "usuario": valor_usuario
            })
        else:
            raise HTTPException(status_code=401, detail={
                "estado": 401, "mensaje": mensaje, "usuario": valor_usuario
            })

    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error al verificar credenciales.", "detalle": str(ex)
        })
