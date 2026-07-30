"""Contrato del servicio específico para rutarol."""

from typing import Protocol, Any, Optional


class IServicioRutaRol(Protocol):
    """Contrato del servicio específico para rutarol."""

    async def listar(
        self, esquema: Optional[str] = None,
        limite: Optional[int] = None
    ) -> list[dict[str, Any]]:
        ...

    async def obtener_por_rol(
        self, rol: str,
        esquema: Optional[str] = None
    ) -> list[dict[str, Any]]:
        ...

    async def crear(
        self, datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> bool:
        ...

    async def eliminar(
        self, ruta: str,
        esquema: Optional[str] = None
    ) -> int:
        ...
