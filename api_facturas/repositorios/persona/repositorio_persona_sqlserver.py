"""Repositorio de persona para SQL Server."""

from repositorios.base_repositorio_sqlserver import BaseRepositorioSqlServer


class RepositorioPersonaSqlServer(BaseRepositorioSqlServer):
    """Acceso a datos de persona en SQL Server."""

    TABLA = "persona"
    CLAVE_PRIMARIA = "codigo"

    async def obtener_todos(self, esquema=None, limite=None):
        """Obtiene todas las personas."""
        return await self._obtener_filas(self.TABLA, esquema, limite)

    async def obtener_por_codigo(self, codigo, esquema=None):
        """Obtiene una persona por su codigo."""
        return await self._obtener_por_clave(
            self.TABLA, self.CLAVE_PRIMARIA, str(codigo), esquema
        )

    async def crear(self, datos, esquema=None):
        """Crea una nueva persona."""
        return await self._crear(self.TABLA, datos, esquema)

    async def actualizar(self, codigo, datos, esquema=None):
        """Actualiza una persona existente."""
        return await self._actualizar(
            self.TABLA, self.CLAVE_PRIMARIA, str(codigo), datos, esquema
        )

    async def eliminar(self, codigo, esquema=None):
        """Elimina una persona por su codigo."""
        return await self._eliminar(
            self.TABLA, self.CLAVE_PRIMARIA, str(codigo), esquema
        )
