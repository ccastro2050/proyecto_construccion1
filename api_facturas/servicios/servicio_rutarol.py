"""Servicio específico para la entidad rutarol."""

from typing import Any


class ServicioRutaRol:
    """Lógica de negocio para rutarol."""

    def __init__(self, repositorio):
        if repositorio is None:
            raise ValueError("repositorio no puede ser None.")
        self._repo = repositorio

    async def listar(self, esquema: str | None = None, limite: int | None = None) -> list[dict[str, Any]]:
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        limite_norm = limite if limite and limite > 0 else None
        return await self._repo.obtener_todos(esquema_norm, limite_norm)

    async def obtener_por_rol(self, rol: str, esquema: str | None = None) -> list[dict[str, Any]]:
        if not rol or not rol.strip():
            raise ValueError("El rol no puede estar vacío.")
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        return await self._repo.obtener_por_rol(rol, esquema_norm)

    async def crear(self, datos: dict[str, Any], esquema: str | None = None) -> bool:
        if not datos:
            raise ValueError("Los datos no pueden estar vacíos.")
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        return await self._repo.crear(datos, esquema_norm)

    async def eliminar(self, ruta: str, esquema: str | None = None) -> int:
        if not ruta or not ruta.strip():
            raise ValueError("La ruta no puede estar vacía.")
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        return await self._repo.eliminar(ruta, esquema_norm)
