"""Contrato del repositorio específico para persona."""
from typing import Protocol, Any, Optional


class IRepositorioPersona(Protocol):
    """Contrato para el repositorio de persona."""

    async def obtener_todos(
        self,
        esquema: Optional[str] = None,
        limite: Optional[int] = None
    ) -> list[dict[str, Any]]:
        """Obtiene todas las personas."""
        ...

    async def obtener_por_codigo(
        self,
        codigo: str,
        esquema: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Obtiene una persona por su código."""
        ...

    async def crear(
        self,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> bool:
        """Crea una nueva persona. Retorna True si se creó."""
        ...

    async def actualizar(
        self,
        codigo: str,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> int:
        """Actualiza una persona. Retorna filas afectadas."""
        ...

    async def eliminar(
        self,
        codigo: str,
        esquema: Optional[str] = None
    ) -> int:
        """Elimina una persona. Retorna filas eliminadas."""
        ...
