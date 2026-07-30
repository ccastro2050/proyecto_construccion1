"""Repositorio de rol para SQL Server."""

from repositorios.base_repositorio_sqlserver import BaseRepositorioSqlServer


class RepositorioRolSqlServer(BaseRepositorioSqlServer):
    """Acceso a datos de rol en SQL Server."""

    TABLA = "rol"
    CLAVE_PRIMARIA = "id"

    async def obtener_todos(self, esquema=None, limite=None):
        """Obtiene todos los roles."""
        return await self._obtener_filas(self.TABLA, esquema, limite)

    async def obtener_por_id(self, id, esquema=None):
        """Obtiene un rol por su id."""
        return await self._obtener_por_clave(
            self.TABLA, self.CLAVE_PRIMARIA, str(id), esquema
        )

    async def crear(self, datos, esquema=None):
        """Crea un nuevo rol."""
        return await self._crear(self.TABLA, datos, esquema)

    async def actualizar(self, id, datos, esquema=None):
        """Actualiza un rol existente."""
        return await self._actualizar(
            self.TABLA, self.CLAVE_PRIMARIA, str(id), datos, esquema
        )

    async def eliminar(self, id, esquema=None):
        """Elimina un rol por su id."""
        return await self._eliminar(
            self.TABLA, self.CLAVE_PRIMARIA, str(id), esquema
        )
