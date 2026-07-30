"""Repositorio de ruta para PostgreSQL."""

from repositorios.base_repositorio_postgresql import BaseRepositorioPostgreSQL


class RepositorioRutaPostgreSQL(BaseRepositorioPostgreSQL):
    """Acceso a datos de ruta en PostgreSQL."""

    TABLA = "ruta"
    CLAVE_PRIMARIA = "ruta"

    async def obtener_todos(self, esquema=None, limite=None):
        """Obtiene todas las rutas."""
        return await self._obtener_filas(self.TABLA, esquema, limite)

    async def obtener_por_ruta(self, ruta, esquema=None):
        """Obtiene una ruta por su valor de ruta."""
        return await self._obtener_por_clave(
            self.TABLA, self.CLAVE_PRIMARIA, str(ruta), esquema
        )

    async def crear(self, datos, esquema=None):
        """Crea una nueva ruta."""
        return await self._crear(self.TABLA, datos, esquema)

    async def actualizar(self, ruta, datos, esquema=None):
        """Actualiza una ruta existente."""
        return await self._actualizar(
            self.TABLA, self.CLAVE_PRIMARIA, str(ruta), datos, esquema
        )

    async def eliminar(self, ruta, esquema=None):
        """Elimina una ruta por su valor de ruta."""
        return await self._eliminar(
            self.TABLA, self.CLAVE_PRIMARIA, str(ruta), esquema
        )
