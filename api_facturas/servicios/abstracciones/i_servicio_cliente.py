"""Contrato del servicio específico para cliente."""

from typing import Protocol, Any, Optional


class IServicioCliente(Protocol):
    """Contrato del servicio específico para cliente."""

    async def listar(
        self, esquema: Optional[str] = None,
        limite: Optional[int] = None
    ) -> list[dict[str, Any]]:
        ...

    async def obtener_por_id(
        self, id: int,
        esquema: Optional[str] = None
    ) -> list[dict[str, Any]]:
        ...

    async def crear(
        self, datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> bool:
        ...

    async def actualizar(
        self, id: int,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> int:
        ...

    async def eliminar(
        self, id: int,
        esquema: Optional[str] = None
    ) -> int:
        ...
