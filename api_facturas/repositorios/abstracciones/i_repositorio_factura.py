"""Contrato del repositorio específico para factura."""
from typing import Protocol, Any, Optional


class IRepositorioFactura(Protocol):
    """Contrato para el repositorio de factura."""

    async def obtener_todos(
        self,
        esquema: Optional[str] = None,
        limite: Optional[int] = None
    ) -> list[dict[str, Any]]:
        """Obtiene todas las facturas."""
        ...

    async def obtener_por_numero(
        self,
        numero: int,
        esquema: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Obtiene una factura por su número."""
        ...

    async def crear(
        self,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> bool:
        """Crea una nueva factura. Retorna True si se creó."""
        ...

    async def actualizar(
        self,
        numero: int,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> int:
        """Actualiza una factura. Retorna filas afectadas."""
        ...

    async def eliminar(
        self,
        numero: int,
        esquema: Optional[str] = None
    ) -> int:
        """Elimina una factura. Retorna filas eliminadas."""
        ...
