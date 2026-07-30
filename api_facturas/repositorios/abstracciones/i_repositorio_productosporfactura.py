"""Contrato del repositorio específico para productos por factura."""
from typing import Protocol, Any, Optional


class IRepositorioProductosPorFactura(Protocol):
    """Contrato para el repositorio de productos por factura."""

    async def obtener_todos(
        self,
        esquema: Optional[str] = None,
        limite: Optional[int] = None
    ) -> list[dict[str, Any]]:
        """Obtiene todos los productos por factura."""
        ...

    async def obtener_por_factura(
        self,
        fknumfactura: int,
        esquema: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Obtiene los productos de una factura por su número."""
        ...

    async def crear(
        self,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> bool:
        """Crea un nuevo producto por factura. Retorna True si se creó."""
        ...

    async def eliminar(
        self,
        fknumfactura: int,
        esquema: Optional[str] = None
    ) -> int:
        """Elimina productos de una factura. Retorna filas eliminadas."""
        ...
