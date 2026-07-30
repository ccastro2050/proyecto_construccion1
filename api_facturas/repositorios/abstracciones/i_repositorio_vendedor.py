"""Contrato del repositorio específico para vendedor."""
from typing import Protocol, Any, Optional


class IRepositorioVendedor(Protocol):
    """Contrato para el repositorio de vendedor."""

    async def obtener_todos(
        self,
        esquema: Optional[str] = None,
        limite: Optional[int] = None
    ) -> list[dict[str, Any]]:
        """Obtiene todos los vendedores."""
        ...

    async def obtener_por_id(
        self,
        id: int,
        esquema: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Obtiene un vendedor por su id."""
        ...

    async def crear(
        self,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> bool:
        """Crea un nuevo vendedor. Retorna True si se creó."""
        ...

    async def actualizar(
        self,
        id: int,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> int:
        """Actualiza un vendedor. Retorna filas afectadas."""
        ...

    async def eliminar(
        self,
        id: int,
        esquema: Optional[str] = None
    ) -> int:
        """Elimina un vendedor. Retorna filas eliminadas."""
        ...
