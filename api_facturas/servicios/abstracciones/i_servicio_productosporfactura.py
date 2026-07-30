"""Contrato del servicio específico para productosporfactura."""

from typing import Protocol, Any, Optional


class IServicioProductosPorFactura(Protocol):
    """Contrato del servicio específico para productosporfactura."""

    async def listar(
        self, esquema: Optional[str] = None,
        limite: Optional[int] = None
    ) -> list[dict[str, Any]]:
        ...

    async def obtener_por_factura(
        self, fknumfactura: int,
        esquema: Optional[str] = None
    ) -> list[dict[str, Any]]:
        ...

    async def crear(
        self, datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> bool:
        ...

    async def eliminar(
        self, fknumfactura: int,
        esquema: Optional[str] = None
    ) -> int:
        ...
