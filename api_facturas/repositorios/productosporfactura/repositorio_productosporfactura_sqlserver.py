"""Repositorio de productosporfactura para SQL Server."""

from repositorios.base_repositorio_sqlserver import BaseRepositorioSqlServer


class RepositorioProductosPorFacturaSqlServer(BaseRepositorioSqlServer):
    """Acceso a datos de productosporfactura en SQL Server."""

    TABLA = "productosporfactura"
    CLAVE_PRIMARIA = "fknumfactura"

    async def obtener_todos(self, esquema=None, limite=None):
        """Obtiene todos los productos por factura."""
        return await self._obtener_filas(self.TABLA, esquema, limite)

    async def obtener_por_factura(self, fknumfactura, esquema=None):
        """Obtiene los productos de una factura por su numero de factura."""
        return await self._obtener_por_clave(
            self.TABLA, "fknumfactura", str(fknumfactura), esquema
        )

    async def crear(self, datos, esquema=None):
        """Crea un nuevo registro de producto por factura."""
        return await self._crear(self.TABLA, datos, esquema)

    async def eliminar(self, fknumfactura, esquema=None):
        """Elimina productos por factura segun su numero de factura."""
        return await self._eliminar(
            self.TABLA, self.CLAVE_PRIMARIA, str(fknumfactura), esquema
        )
