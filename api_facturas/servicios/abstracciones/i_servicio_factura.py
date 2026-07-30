"""Contrato del servicio específico para factura."""

from typing import Protocol, Any, Optional


class IServicioFactura(Protocol):
    """Contrato del servicio específico para factura."""

    async def listar(
        self, esquema: Optional[str] = None,
        limite: Optional[int] = None
    ) -> list[dict[str, Any]]:
        ...

    async def obtener_por_numero(
        self, numero: int,
        esquema: Optional[str] = None
    ) -> list[dict[str, Any]]:
        ...

    async def crear(
        self, datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> bool:
        ...

    async def actualizar(
        self, numero: int,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> int:
        ...

    async def eliminar(
        self, numero: int,
        esquema: Optional[str] = None
    ) -> int:
        ...
