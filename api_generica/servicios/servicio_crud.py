"""Lógica de negocio para operaciones CRUD."""

from typing import Any
from repositorios.abstracciones.i_repositorio_lectura_tabla import (
    IRepositorioLecturaTabla
)
from servicios.utilidades.encriptacion_bcrypt import verificar


class ServicioCrud:
    """Coordina operaciones CRUD aplicando reglas de negocio."""

    def __init__(self, repositorio_lectura: IRepositorioLecturaTabla):
        if repositorio_lectura is None:
            raise ValueError("repositorio_lectura no puede ser None.")
        self._repositorio = repositorio_lectura

    async def listar(
        self, nombre_tabla: str, esquema: str | None = None,
        limite: int | None = None
    ) -> list[dict[str, Any]]:
        if not nombre_tabla or not nombre_tabla.strip():
            raise ValueError("El nombre de la tabla no puede estar vacío.")

        esquema_norm = (esquema.strip()
                        if esquema and esquema.strip() else None)
        limite_norm = limite if limite and limite > 0 else None

        return await self._repositorio.obtener_filas(
            nombre_tabla=nombre_tabla,
            esquema=esquema_norm,
            limite=limite_norm
        )

    async def obtener_por_clave(
        self, nombre_tabla: str, nombre_clave: str, valor: str,
        esquema: str | None = None
    ) -> list[dict[str, Any]]:
        if not nombre_tabla or not nombre_tabla.strip():
            raise ValueError("El nombre de la tabla no puede estar vacío.")
        if not nombre_clave or not nombre_clave.strip():
            raise ValueError("El nombre de la clave no puede estar vacío.")
        if not valor or not valor.strip():
            raise ValueError("El valor no puede estar vacío.")

        esquema_norm = (esquema.strip()
                        if esquema and esquema.strip() else None)

        return await self._repositorio.obtener_por_clave(
            nombre_tabla=nombre_tabla,
            nombre_clave=nombre_clave,
            valor=valor,
            esquema=esquema_norm
        )

    async def crear(
        self, nombre_tabla: str, datos: dict[str, Any],
        esquema: str | None = None, campos_encriptar: str | None = None
    ) -> bool:
        if not nombre_tabla or not nombre_tabla.strip():
            raise ValueError("El nombre de la tabla no puede estar vacío.")
        if not datos:
            raise ValueError("Los datos no pueden estar vacíos.")

        esquema_norm = (esquema.strip()
                        if esquema and esquema.strip() else None)

        return await self._repositorio.crear(
            nombre_tabla=nombre_tabla,
            datos=datos,
            esquema=esquema_norm,
            campos_encriptar=campos_encriptar
        )

    async def actualizar(
        self, nombre_tabla: str, nombre_clave: str, valor_clave: str,
        datos: dict[str, Any], esquema: str | None = None,
        campos_encriptar: str | None = None
    ) -> int:
        if not nombre_tabla or not nombre_tabla.strip():
            raise ValueError("El nombre de la tabla no puede estar vacío.")
        if not nombre_clave or not nombre_clave.strip():
            raise ValueError("El nombre de la clave no puede estar vacío.")
        if not valor_clave or not valor_clave.strip():
            raise ValueError("El valor de la clave no puede estar vacío.")
        if not datos:
            raise ValueError("Los datos no pueden estar vacíos.")

        esquema_norm = (esquema.strip()
                        if esquema and esquema.strip() else None)

        return await self._repositorio.actualizar(
            nombre_tabla=nombre_tabla,
            nombre_clave=nombre_clave,
            valor_clave=valor_clave,
            datos=datos,
            esquema=esquema_norm,
            campos_encriptar=campos_encriptar
        )

    async def eliminar(
        self, nombre_tabla: str, nombre_clave: str, valor_clave: str,
        esquema: str | None = None
    ) -> int:
        if not nombre_tabla or not nombre_tabla.strip():
            raise ValueError("El nombre de la tabla no puede estar vacío.")
        if not nombre_clave or not nombre_clave.strip():
            raise ValueError("El nombre de la clave no puede estar vacío.")
        if not valor_clave or not valor_clave.strip():
            raise ValueError("El valor de la clave no puede estar vacío.")

        esquema_norm = (esquema.strip()
                        if esquema and esquema.strip() else None)

        return await self._repositorio.eliminar(
            nombre_tabla=nombre_tabla,
            nombre_clave=nombre_clave,
            valor_clave=valor_clave,
            esquema=esquema_norm
        )

    async def verificar_contrasena(
        self, nombre_tabla: str, campo_usuario: str,
        campo_contrasena: str, valor_usuario: str,
        valor_contrasena: str, esquema: str | None = None
    ) -> tuple[int, str]:
        if not nombre_tabla or not nombre_tabla.strip():
            raise ValueError("El nombre de la tabla no puede estar vacío.")
        if not campo_usuario or not campo_usuario.strip():
            raise ValueError("El campo de usuario no puede estar vacío.")
        if not campo_contrasena or not campo_contrasena.strip():
            raise ValueError(
                "El campo de contraseña no puede estar vacío."
            )
        if not valor_usuario or not valor_usuario.strip():
            raise ValueError("El usuario no puede estar vacío.")
        if not valor_contrasena or not valor_contrasena.strip():
            raise ValueError("La contraseña no puede estar vacía.")

        esquema_norm = (esquema.strip()
                        if esquema and esquema.strip() else None)

        hash_almacenado = await self._repositorio.obtener_hash_contrasena(
            nombre_tabla=nombre_tabla,
            campo_usuario=campo_usuario,
            campo_contrasena=campo_contrasena,
            valor_usuario=valor_usuario,
            esquema=esquema_norm
        )

        if hash_almacenado is None:
            return (404, "Usuario no encontrado.")

        if verificar(valor_contrasena, hash_almacenado):
            return (200, "Contraseña válida.")
        else:
            return (401, "Contraseña incorrecta.")
