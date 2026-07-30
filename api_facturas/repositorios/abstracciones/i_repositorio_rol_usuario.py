"""Contrato del repositorio específico para rol de usuario."""
from typing import Protocol, Any, Optional


class IRepositorioRolUsuario(Protocol):
    """Contrato para el repositorio de rol de usuario."""

    async def obtener_todos(
        self,
        esquema: Optional[str] = None,
        limite: Optional[int] = None
    ) -> list[dict[str, Any]]:
        """Obtiene todos los roles de usuario."""
        ...

    async def obtener_por_email(
        self,
        fkemail: str,
        esquema: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Obtiene los roles de un usuario por su email."""
        ...

    async def obtener_por_rol(
        self,
        fkidrol: int,
        esquema: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Obtiene los usuarios de un rol por su id."""
        ...

    async def crear(
        self,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> bool:
        """Crea una nueva asignación de rol a usuario. Retorna True si se creó."""
        ...

    async def eliminar(
        self,
        fkemail: str,
        esquema: Optional[str] = None
    ) -> int:
        """Elimina una asignación de rol a usuario. Retorna filas eliminadas."""
        ...
