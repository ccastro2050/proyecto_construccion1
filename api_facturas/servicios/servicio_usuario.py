"""Servicio específico para la entidad usuario."""

from typing import Any


class ServicioUsuario:
    """Lógica de negocio para usuario."""

    def __init__(self, repositorio):
        if repositorio is None:
            raise ValueError("repositorio no puede ser None.")
        self._repo = repositorio

    async def listar(self, esquema: str | None = None, limite: int | None = None) -> list[dict[str, Any]]:
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        limite_norm = limite if limite and limite > 0 else None
        return await self._repo.obtener_todos(esquema_norm, limite_norm)

    async def obtener_por_email(self, email: str, esquema: str | None = None) -> list[dict[str, Any]]:
        if not email or not email.strip():
            raise ValueError("El email no puede estar vacío.")
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        return await self._repo.obtener_por_email(email, esquema_norm)

    async def crear(self, datos: dict[str, Any], esquema: str | None = None) -> bool:
        if not datos:
            raise ValueError("Los datos no pueden estar vacíos.")
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        return await self._repo.crear(datos, esquema_norm)

    async def actualizar(self, email: str, datos: dict[str, Any], esquema: str | None = None) -> int:
        if not email or not email.strip():
            raise ValueError("El email no puede estar vacío.")
        if not datos:
            raise ValueError("Los datos no pueden estar vacíos.")
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        return await self._repo.actualizar(email, datos, esquema_norm)

    async def eliminar(self, email: str, esquema: str | None = None) -> int:
        if not email or not email.strip():
            raise ValueError("El email no puede estar vacío.")
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        return await self._repo.eliminar(email, esquema_norm)

    async def verificar_contrasena(self, email: str, contrasena: str, esquema: str | None = None) -> tuple[int, str]:
        if not email or not email.strip():
            raise ValueError("El email no puede estar vacío.")
        if not contrasena or not contrasena.strip():
            raise ValueError("La contraseña no puede estar vacía.")
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        hash_almacenado = await self._repo.obtener_hash_contrasena(email, esquema_norm)
        if hash_almacenado is None:
            return (404, "Usuario no encontrado.")
        from servicios.utilidades.encriptacion_bcrypt import verificar
        if verificar(contrasena, hash_almacenado):
            return (200, "Contraseña válida.")
        return (401, "Contraseña incorrecta.")
