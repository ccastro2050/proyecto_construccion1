"""Contrato para la lógica de negocio CRUD."""

from typing import Protocol, Any


class IServicioCrud(Protocol):
    """Contrato para un servicio CRUD genérico."""

    async def listar(self, nombre_tabla: str, esquema: str | None = None,
                     limite: int | None = None) -> list[dict[str, Any]]:
        ...

    async def obtener_por_clave(self, nombre_tabla: str,
                                 nombre_clave: str, valor: str,
                                 esquema: str | None = None
                                 ) -> list[dict[str, Any]]:
        ...

    async def crear(self, nombre_tabla: str, datos: dict[str, Any],
                    esquema: str | None = None,
                    campos_encriptar: str | None = None) -> bool:
        ...

    async def actualizar(self, nombre_tabla: str, nombre_clave: str,
                         valor_clave: str, datos: dict[str, Any],
                         esquema: str | None = None,
                         campos_encriptar: str | None = None) -> int:
        ...

    async def eliminar(self, nombre_tabla: str, nombre_clave: str,
                       valor_clave: str,
                       esquema: str | None = None) -> int:
        ...

    async def verificar_contrasena(
        self, nombre_tabla: str, campo_usuario: str,
        campo_contrasena: str, valor_usuario: str,
        valor_contrasena: str, esquema: str | None = None
    ) -> tuple[int, str]:
        ...
