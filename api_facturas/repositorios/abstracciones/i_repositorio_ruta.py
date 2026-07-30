"""Contrato del repositorio específico para ruta."""
from typing import Protocol, Any, Optional


class IRepositorioRuta(Protocol):
    """Contrato para el repositorio de ruta."""

    async def obtener_todos(
        self,
        esquema: Optional[str] = None,
        limite: Optional[int] = None
    ) -> list[dict[str, Any]]:
        """Obtiene todas las rutas."""
        ...

    async def obtener_por_ruta(
        self,
        ruta: str,
        esquema: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Obtiene una ruta por su valor."""
        ...

    async def crear(
        self,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> bool:
        """Crea una nueva ruta. Retorna True si se creó."""
        ...

    async def actualizar(
        self,
        ruta: str,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> int:
        """Actualiza una ruta. Retorna filas afectadas."""
        ...

    async def eliminar(
        self,
        ruta: str,
        esquema: Optional[str] = None
    ) -> int:
        """Elimina una ruta. Retorna filas eliminadas."""
        ...
