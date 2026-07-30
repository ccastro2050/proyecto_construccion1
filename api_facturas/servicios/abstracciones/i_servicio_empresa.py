"""Contrato del servicio específico para empresa."""

from typing import Protocol, Any, Optional


class IServicioEmpresa(Protocol):
    """Contrato del servicio específico para empresa."""

    async def listar(
        self, esquema: Optional[str] = None,
        limite: Optional[int] = None
    ) -> list[dict[str, Any]]:
        ...

    async def obtener_por_codigo(
        self, codigo: str,
        esquema: Optional[str] = None
    ) -> list[dict[str, Any]]:
        ...

    async def crear(
        self, datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> bool:
        ...

    async def actualizar(
        self, codigo: str,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> int:
        ...

    async def eliminar(
        self, codigo: str,
        esquema: Optional[str] = None
    ) -> int:
        ...
