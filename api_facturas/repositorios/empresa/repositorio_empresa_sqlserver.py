"""Repositorio de empresa para SQL Server."""

from repositorios.base_repositorio_sqlserver import BaseRepositorioSqlServer


class RepositorioEmpresaSqlServer(BaseRepositorioSqlServer):
    """Acceso a datos de empresa en SQL Server."""

    TABLA = "empresa"
    CLAVE_PRIMARIA = "codigo"

    async def obtener_todos(self, esquema=None, limite=None):
        """Obtiene todas las empresas."""
        return await self._obtener_filas(self.TABLA, esquema, limite)

    async def obtener_por_codigo(self, codigo, esquema=None):
        """Obtiene una empresa por su codigo."""
        return await self._obtener_por_clave(
            self.TABLA, self.CLAVE_PRIMARIA, str(codigo), esquema
        )

    async def crear(self, datos, esquema=None):
        """Crea una nueva empresa."""
        return await self._crear(self.TABLA, datos, esquema)

    async def actualizar(self, codigo, datos, esquema=None):
        """Actualiza una empresa existente."""
        return await self._actualizar(
            self.TABLA, self.CLAVE_PRIMARIA, str(codigo), datos, esquema
        )

    async def eliminar(self, codigo, esquema=None):
        """Elimina una empresa por su codigo."""
        return await self._eliminar(
            self.TABLA, self.CLAVE_PRIMARIA, str(codigo), esquema
        )
