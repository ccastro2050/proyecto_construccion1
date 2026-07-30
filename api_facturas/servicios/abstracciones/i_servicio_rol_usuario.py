"""Contrato del servicio específico para rol_usuario."""

from typing import Protocol, Any, Optional


class IServicioRolUsuario(Protocol):
    """Contrato del servicio específico para rol_usuario."""

    async def listar(
        self, esquema: Optional[str] = None,
        limite: Optional[int] = None
    ) -> list[dict[str, Any]]:
        ...

    async def obtener_por_email(
        self, fkemail: str,
        esquema: Optional[str] = None
    ) -> list[dict[str, Any]]:
        ...

    async def obtener_por_rol(
        self, fkidrol: int,
        esquema: Optional[str] = None
    ) -> list[dict[str, Any]]:
        ...

    async def crear(
        self, datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> bool:
        ...

    async def eliminar(
        self, fkemail: str,
        esquema: Optional[str] = None
    ) -> int:
        ...
