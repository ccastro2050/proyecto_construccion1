"""Contrato del repositorio específico para empresa."""
from typing import Protocol, Any, Optional


class IRepositorioEmpresa(Protocol):
    """Contrato para el repositorio de empresa."""

    async def obtener_todos(
        self,
        esquema: Optional[str] = None,
        limite: Optional[int] = None
    ) -> list[dict[str, Any]]:
        """Obtiene todas las empresas."""
        ...

    async def obtener_por_codigo(
        self,
        codigo: str,
        esquema: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Obtiene una empresa por su código."""
        ...

    async def crear(
        self,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> bool:
        """Crea una nueva empresa. Retorna True si se creó."""
        ...

    async def actualizar(
        self,
        codigo: str,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> int:
        """Actualiza una empresa. Retorna filas afectadas."""
        ...

    async def eliminar(
        self,
        codigo: str,
        esquema: Optional[str] = None
    ) -> int:
        """Elimina una empresa. Retorna filas eliminadas."""
        ...
