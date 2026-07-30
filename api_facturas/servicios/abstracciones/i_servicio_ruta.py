"""Contrato del servicio específico para ruta."""

from typing import Protocol, Any, Optional


class IServicioRuta(Protocol):
    """Contrato del servicio específico para ruta."""

    async def listar(
        self, esquema: Optional[str] = None,
        limite: Optional[int] = None
    ) -> list[dict[str, Any]]:
        ...

    async def obtener_por_ruta(
        self, ruta: str,
        esquema: Optional[str] = None
    ) -> list[dict[str, Any]]:
        ...

    async def crear(
        self, datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> bool:
        ...

    async def actualizar(
        self, ruta: str,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> int:
        ...

    async def eliminar(
        self, ruta: str,
        esquema: Optional[str] = None
    ) -> int:
        ...
