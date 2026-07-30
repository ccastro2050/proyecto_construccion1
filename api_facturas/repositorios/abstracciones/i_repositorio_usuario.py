"""Contrato del repositorio específico para usuario."""
from typing import Protocol, Any, Optional


class IRepositorioUsuario(Protocol):
    """Contrato para el repositorio de usuario."""

    async def obtener_todos(
        self,
        esquema: Optional[str] = None,
        limite: Optional[int] = None
    ) -> list[dict[str, Any]]:
        """Obtiene todos los usuarios."""
        ...

    async def obtener_por_email(
        self,
        email: str,
        esquema: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Obtiene un usuario por su email."""
        ...

    async def crear(
        self,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> bool:
        """Crea un nuevo usuario. Retorna True si se creó."""
        ...

    async def actualizar(
        self,
        email: str,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> int:
        """Actualiza un usuario. Retorna filas afectadas."""
        ...

    async def eliminar(
        self,
        email: str,
        esquema: Optional[str] = None
    ) -> int:
        """Elimina un usuario. Retorna filas eliminadas."""
        ...

    async def obtener_hash_contrasena(
        self,
        email: str,
        esquema: Optional[str] = None
    ) -> Optional[str]:
        """Obtiene el hash de contraseña almacenado para un usuario."""
        ...
