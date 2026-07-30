"""Repositorio de cliente para PostgreSQL."""

from repositorios.base_repositorio_postgresql import BaseRepositorioPostgreSQL


class RepositorioClientePostgreSQL(BaseRepositorioPostgreSQL):
    """Acceso a datos de cliente en PostgreSQL."""

    TABLA = "cliente"
    CLAVE_PRIMARIA = "id"

    async def obtener_todos(self, esquema=None, limite=None):
        """Obtiene todos los clientes."""
        return await self._obtener_filas(self.TABLA, esquema, limite)

    async def obtener_por_id(self, id, esquema=None):
        """Obtiene un cliente por su id."""
        return await self._obtener_por_clave(
            self.TABLA, self.CLAVE_PRIMARIA, str(id), esquema
        )

    async def crear(self, datos, esquema=None):
        """Crea un nuevo cliente."""
        return await self._crear(self.TABLA, datos, esquema)

    async def actualizar(self, id, datos, esquema=None):
        """Actualiza un cliente existente."""
        return await self._actualizar(
            self.TABLA, self.CLAVE_PRIMARIA, str(id), datos, esquema
        )

    async def eliminar(self, id, esquema=None):
        """Elimina un cliente por su id."""
        return await self._eliminar(
            self.TABLA, self.CLAVE_PRIMARIA, str(id), esquema
        )
