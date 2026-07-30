"""Repositorio de factura para SQL Server."""

from repositorios.base_repositorio_sqlserver import BaseRepositorioSqlServer


class RepositorioFacturaSqlServer(BaseRepositorioSqlServer):
    """Acceso a datos de factura en SQL Server."""

    TABLA = "factura"
    CLAVE_PRIMARIA = "numero"

    async def obtener_todos(self, esquema=None, limite=None):
        """Obtiene todas las facturas."""
        return await self._obtener_filas(self.TABLA, esquema, limite)

    async def obtener_por_numero(self, numero, esquema=None):
        """Obtiene una factura por su numero."""
        return await self._obtener_por_clave(
            self.TABLA, self.CLAVE_PRIMARIA, str(numero), esquema
        )

    async def crear(self, datos, esquema=None):
        """Crea una nueva factura."""
        return await self._crear(self.TABLA, datos, esquema)

    async def actualizar(self, numero, datos, esquema=None):
        """Actualiza una factura existente."""
        return await self._actualizar(
            self.TABLA, self.CLAVE_PRIMARIA, str(numero), datos, esquema
        )

    async def eliminar(self, numero, esquema=None):
        """Elimina una factura por su numero."""
        return await self._eliminar(
            self.TABLA, self.CLAVE_PRIMARIA, str(numero), esquema
        )
