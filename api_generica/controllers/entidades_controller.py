"""
entidades_controller.py — Controlador HTTP para operaciones CRUD sobre cualquier tabla.

Esta es la capa de presentación: recibe peticiones HTTP, las valida,
delega al servicio la lógica real, y retorna respuestas JSON.

Endpoints disponibles:
- GET    /api/{tabla}                         → Listar registros
- GET    /api/{tabla}/{clave}/{valor}          → Filtrar por clave
- POST   /api/{tabla}                         → Crear registro
- PUT    /api/{tabla}/{clave}/{valor}          → Actualizar registro
- DELETE /api/{tabla}/{clave}/{valor}          → Eliminar registro
- POST   /api/{tabla}/verificar-contrasena     → Verificar credenciales
"""

from typing import Any

from fastapi import APIRouter, HTTPException, Query, Response

from servicios.fabrica_repositorios import crear_servicio_crud


# Router de FastAPI (agrupa todos los endpoints bajo /api)
router = APIRouter(prefix="/api", tags=["Entidades"])


# =========================================================================
# GET /api/{tabla} — Listar registros
# =========================================================================

@router.get("/{tabla}")
async def listar(
    tabla: str,
    esquema: str | None = Query(default=None, description="Esquema de la base de datos"),
    limite: int | None = Query(default=None, description="Límite de registros a devolver")
):
    """
    Lista registros de cualquier tabla.
    Ejemplos: GET /api/usuarios, GET /api/productos?limite=50
    """
    try:
        servicio = crear_servicio_crud()
        filas = await servicio.listar(tabla, esquema, limite)

        # Si no hay datos, retornar 204 (sin contenido)
        if len(filas) == 0:
            return Response(status_code=204)

        return {
            "tabla": tabla,
            "esquema": esquema or "por defecto",
            "limite": limite,
            "total": len(filas),
            "datos": filas
        }

    except ValueError as ex:
        raise HTTPException(status_code=400, detail={
            "estado": 400, "mensaje": "Parámetros inválidos.", "detalle": str(ex)
        })
    except PermissionError as ex:
        raise HTTPException(status_code=403, detail={
            "estado": 403, "mensaje": "Acceso denegado.", "detalle": str(ex)
        })
    except LookupError as ex:
        raise HTTPException(status_code=404, detail={
            "estado": 404, "mensaje": "Recurso no encontrado.", "detalle": str(ex)
        })
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })


# =========================================================================
# GET /api/{tabla}/{nombre_clave}/{valor} — Filtrar por clave
# =========================================================================

@router.get("/{tabla}/{nombre_clave}/{valor}")
async def obtener_por_clave(
    tabla: str,
    nombre_clave: str,
    valor: str,
    esquema: str | None = Query(default=None, description="Esquema de la base de datos")
):
    """
    Obtiene registros filtrados por un valor de clave.
    Ejemplo: GET /api/factura/numero/1
    """
    try:
        servicio = crear_servicio_crud()
        filas = await servicio.obtener_por_clave(tabla, nombre_clave, valor, esquema)

        if len(filas) == 0:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No se encontró ningún registro con {nombre_clave} = {valor} en {tabla}"
            })

        return {
            "tabla": tabla,
            "esquema": esquema or "por defecto",
            "filtro": f"{nombre_clave} = {valor}",
            "total": len(filas),
            "datos": filas
        }

    except HTTPException:
        raise
    except PermissionError as ex:
        raise HTTPException(status_code=403, detail={
            "estado": 403, "mensaje": "Acceso denegado.", "detalle": str(ex)
        })
    except ValueError as ex:
        raise HTTPException(status_code=400, detail={
            "estado": 400, "mensaje": "Parámetros inválidos.", "detalle": str(ex)
        })
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })


# =========================================================================
# POST /api/{tabla} — Crear registro
# =========================================================================

@router.post("/{tabla}")
async def crear(
    tabla: str,
    datos_entidad: dict[str, Any],
    esquema: str | None = Query(default=None, description="Esquema de la base de datos"),
    campos_encriptar: str | None = Query(default=None, description="Campos a encriptar con BCrypt, separados por coma")
):
    """
    Crea un nuevo registro en la tabla.
    El body es un JSON con los campos y valores.
    """
    try:
        if not datos_entidad:
            raise HTTPException(status_code=400, detail={
                "estado": 400, "mensaje": "Los datos no pueden estar vacíos."
            })

        servicio = crear_servicio_crud()
        creado = await servicio.crear(tabla, datos_entidad, esquema, campos_encriptar)

        if creado:
            return {
                "estado": 200,
                "mensaje": "Registro creado exitosamente.",
                "tabla": tabla,
                "esquema": esquema or "por defecto"
            }
        else:
            raise HTTPException(status_code=500, detail={
                "estado": 500, "mensaje": "No se pudo crear el registro."
            })

    except HTTPException:
        raise
    except PermissionError as ex:
        raise HTTPException(status_code=403, detail={
            "estado": 403, "mensaje": "Acceso denegado.", "detalle": str(ex)
        })
    except ValueError as ex:
        raise HTTPException(status_code=400, detail={
            "estado": 400, "mensaje": "Datos inválidos.", "detalle": str(ex)
        })
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })


# =========================================================================
# PUT /api/{tabla}/{nombre_clave}/{valor_clave} — Actualizar registro
# =========================================================================

@router.put("/{tabla}/{nombre_clave}/{valor_clave}")
async def actualizar(
    tabla: str,
    nombre_clave: str,
    valor_clave: str,
    datos_entidad: dict[str, Any],
    esquema: str | None = Query(default=None, description="Esquema de la base de datos"),
    campos_encriptar: str | None = Query(default=None, description="Campos a encriptar con BCrypt")
):
    """
    Actualiza un registro existente.
    Ejemplo: PUT /api/usuario/email/juan@test.com con body JSON
    """
    try:
        if not datos_entidad:
            raise HTTPException(status_code=400, detail={
                "estado": 400, "mensaje": "Los datos de actualización no pueden estar vacíos."
            })

        servicio = crear_servicio_crud()
        filas_afectadas = await servicio.actualizar(
            tabla, nombre_clave, valor_clave, datos_entidad, esquema, campos_encriptar
        )

        if filas_afectadas > 0:
            return {
                "estado": 200,
                "mensaje": "Registro actualizado exitosamente.",
                "tabla": tabla,
                "filtro": f"{nombre_clave} = {valor_clave}",
                "filasAfectadas": filas_afectadas
            }
        else:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No existe un registro con {nombre_clave} = {valor_clave} en {tabla}"
            })

    except HTTPException:
        raise
    except PermissionError as ex:
        raise HTTPException(status_code=403, detail={
            "estado": 403, "mensaje": "Acceso denegado.", "detalle": str(ex)
        })
    except ValueError as ex:
        raise HTTPException(status_code=400, detail={
            "estado": 400, "mensaje": "Parámetros inválidos.", "detalle": str(ex)
        })
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })


# =========================================================================
# DELETE /api/{tabla}/{nombre_clave}/{valor_clave} — Eliminar registro
# =========================================================================

@router.delete("/{tabla}/{nombre_clave}/{valor_clave}")
async def eliminar(
    tabla: str,
    nombre_clave: str,
    valor_clave: str,
    esquema: str | None = Query(default=None, description="Esquema de la base de datos")
):
    """
    Elimina un registro de la tabla.
    Ejemplo: DELETE /api/producto/codigo/PRD001
    """
    try:
        servicio = crear_servicio_crud()
        filas_eliminadas = await servicio.eliminar(tabla, nombre_clave, valor_clave, esquema)

        if filas_eliminadas > 0:
            return {
                "estado": 200,
                "mensaje": "Registro eliminado exitosamente.",
                "tabla": tabla,
                "filtro": f"{nombre_clave} = {valor_clave}",
                "filasEliminadas": filas_eliminadas
            }
        else:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No existe un registro con {nombre_clave} = {valor_clave} en {tabla}"
            })

    except HTTPException:
        raise
    except PermissionError as ex:
        raise HTTPException(status_code=403, detail={
            "estado": 403, "mensaje": "Acceso denegado.", "detalle": str(ex)
        })
    except ValueError as ex:
        raise HTTPException(status_code=400, detail={
            "estado": 400, "mensaje": "Parámetros inválidos.", "detalle": str(ex)
        })
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })


# =========================================================================
# POST /api/{tabla}/verificar-contrasena — Verificar credenciales
# =========================================================================

@router.post("/{tabla}/verificar-contrasena")
async def verificar_contrasena(
    tabla: str,
    campo_usuario: str = Query(..., description="Nombre del campo de usuario"),
    campo_contrasena: str = Query(..., description="Nombre del campo de contraseña"),
    valor_usuario: str = Query(..., description="Valor del usuario"),
    valor_contrasena: str = Query(..., description="Contraseña a verificar"),
    esquema: str | None = Query(default=None, description="Esquema de la base de datos")
):
    """
    Verifica credenciales de un usuario contra la base de datos usando BCrypt.
    Ejemplo: POST /api/usuario/verificar-contrasena?campo_usuario=email&campo_contrasena=contrasena&valor_usuario=test@test.com&valor_contrasena=123456
    """
    try:
        servicio = crear_servicio_crud()
        codigo, mensaje = await servicio.verificar_contrasena(
            tabla, campo_usuario, campo_contrasena, valor_usuario, valor_contrasena, esquema
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
    except PermissionError as ex:
        raise HTTPException(status_code=403, detail={
            "estado": 403, "mensaje": "Acceso denegado.", "detalle": str(ex)
        })
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno al verificar credenciales.", "detalle": str(ex)
        })
