"""Contrato del repositorio específico para ruta por rol."""
from typing import Protocol, Any, Optional


class IRepositorioRutaRol(Protocol):
    """Contrato para el repositorio de ruta por rol."""

    async def obtener_todos(
        self,
        esquema: Optional[str] = None,
        limite: Optional[int] = None
    ) -> list[dict[str, Any]]:
        """Obtiene todas las rutas por rol."""
        ...

    async def obtener_por_rol(
        self,
        rol: str,
        esquema: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Obtiene las rutas de un rol."""
        ...

    async def crear(
        self,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> bool:
        """Crea una nueva asignación de ruta a rol. Retorna True si se creó."""
        ...

    async def eliminar(
        self,
        ruta: str,
        esquema: Optional[str] = None
    ) -> int:
        """Elimina una asignación de ruta a rol. Retorna filas eliminadas."""
        ...
