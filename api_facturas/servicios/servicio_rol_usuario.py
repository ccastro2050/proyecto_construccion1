"""Servicio específico para la entidad rol_usuario."""

from typing import Any


class ServicioRolUsuario:
    """Lógica de negocio para rol_usuario."""

    def __init__(self, repositorio):
        if repositorio is None:
            raise ValueError("repositorio no puede ser None.")
        self._repo = repositorio

    async def listar(self, esquema: str | None = None, limite: int | None = None) -> list[dict[str, Any]]:
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        limite_norm = limite if limite and limite > 0 else None
        return await self._repo.obtener_todos(esquema_norm, limite_norm)

    async def obtener_por_email(self, fkemail: str, esquema: str | None = None) -> list[dict[str, Any]]:
        if not fkemail or not fkemail.strip():
            raise ValueError("El email no puede estar vacío.")
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        return await self._repo.obtener_por_email(fkemail, esquema_norm)

    async def obtener_por_rol(self, fkidrol: int, esquema: str | None = None) -> list[dict[str, Any]]:
        if fkidrol is None:
            raise ValueError("El id del rol no puede estar vacío.")
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        return await self._repo.obtener_por_rol(fkidrol, esquema_norm)

    async def crear(self, datos: dict[str, Any], esquema: str | None = None) -> bool:
        if not datos:
            raise ValueError("Los datos no pueden estar vacíos.")
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        return await self._repo.crear(datos, esquema_norm)

    async def eliminar(self, fkemail: str, esquema: str | None = None) -> int:
        if not fkemail or not fkemail.strip():
            raise ValueError("El email no puede estar vacío.")
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        return await self._repo.eliminar(fkemail, esquema_norm)
