"""Contrato del repositorio específico para rol."""
from typing import Protocol, Any, Optional


class IRepositorioRol(Protocol):
    """Contrato para el repositorio de rol."""

    async def obtener_todos(
        self,
        esquema: Optional[str] = None,
        limite: Optional[int] = None
    ) -> list[dict[str, Any]]:
        """Obtiene todos los roles."""
        ...

    async def obtener_por_id(
        self,
        id: int,
        esquema: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Obtiene un rol por su id."""
        ...

    async def crear(
        self,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> bool:
        """Crea un nuevo rol. Retorna True si se creó."""
        ...

    async def actualizar(
        self,
        id: int,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> int:
        """Actualiza un rol. Retorna filas afectadas."""
        ...

    async def eliminar(
        self,
        id: int,
        esquema: Optional[str] = None
    ) -> int:
        """Elimina un rol. Retorna filas eliminadas."""
        ...
