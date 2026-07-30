"""
i_repositorio_lectura_tabla.py — Contrato (interfaz) para acceso a datos.

Define QUÉ operaciones puede hacer un repositorio, sin importar
qué base de datos se use por debajo. Cada proveedor (PostgreSQL,
SQL Server, MySQL) implementa estos métodos a su manera.
"""

from typing import Protocol, Optional


class IRepositorioLecturaTabla(Protocol):
    """
    Contrato para repositorios CRUD genéricos.

    Cualquier clase que implemente estos métodos puede usarse
    como repositorio, sin necesidad de heredar de esta clase.
    """

    async def obtener_filas(
        self,
        nombre_tabla: str,
        esquema: Optional[str] = None,
        limite: Optional[int] = None
    ) -> list[dict[str, object]]:
        """Obtiene filas de una tabla. Retorna lista de diccionarios."""
        ...

    async def obtener_por_clave(
        self,
        nombre_tabla: str,
        nombre_clave: str,
        valor: str,
        esquema: Optional[str] = None
    ) -> list[dict[str, object]]:
        """Obtiene filas filtradas por una columna y valor."""
        ...

    async def crear(
        self,
        nombre_tabla: str,
        datos: dict[str, object],
        esquema: Optional[str] = None,
        campos_encriptar: Optional[str] = None
    ) -> bool:
        """Inserta un nuevo registro. Retorna True si se creó."""
        ...

    async def actualizar(
        self,
        nombre_tabla: str,
        nombre_clave: str,
        valor_clave: str,
        datos: dict[str, object],
        esquema: Optional[str] = None,
        campos_encriptar: Optional[str] = None
    ) -> int:
        """Actualiza un registro. Retorna filas afectadas."""
        ...

    async def eliminar(
        self,
        nombre_tabla: str,
        nombre_clave: str,
        valor_clave: str,
        esquema: Optional[str] = None
    ) -> int:
        """Elimina un registro. Retorna filas eliminadas."""
        ...

    async def obtener_hash_contrasena(
        self,
        nombre_tabla: str,
        campo_usuario: str,
        campo_contrasena: str,
        valor_usuario: str,
        esquema: Optional[str] = None
    ) -> Optional[str]:
        """Obtiene el hash de contraseña almacenado para un usuario."""
        ...
