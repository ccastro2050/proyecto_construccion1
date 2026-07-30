"""Contrato del repositorio específico para cliente."""
from typing import Protocol, Any, Optional


class IRepositorioCliente(Protocol):
    """Contrato para el repositorio de cliente."""

    async def obtener_todos(
        self,
        esquema: Optional[str] = None,
        limite: Optional[int] = None
    ) -> list[dict[str, Any]]:
        """Obtiene todos los clientes."""
        ...

    async def obtener_por_id(
        self,
        id: int,
        esquema: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Obtiene un cliente por su id."""
        ...

    async def crear(
        self,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> bool:
        """Crea un nuevo cliente. Retorna True si se creó."""
        ...

    async def actualizar(
        self,
        id: int,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> int:
        """Actualiza un cliente. Retorna filas afectadas."""
        ...

    async def eliminar(
        self,
        id: int,
        esquema: Optional[str] = None
    ) -> int:
        """Elimina un cliente. Retorna filas eliminadas."""
        ...
