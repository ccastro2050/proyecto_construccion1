"""Repositorio de rutarol para SQL Server."""

from repositorios.base_repositorio_sqlserver import BaseRepositorioSqlServer


class RepositorioRutaRolSqlServer(BaseRepositorioSqlServer):
    """Acceso a datos de rutarol en SQL Server."""

    TABLA = "rutarol"
    CLAVE_PRIMARIA = "ruta"

    async def obtener_todos(self, esquema=None, limite=None):
        """Obtiene todas las asignaciones de ruta a rol."""
        return await self._obtener_filas(self.TABLA, esquema, limite)

    async def obtener_por_ruta(self, ruta, esquema=None):
        """Obtiene las asignaciones por ruta."""
        return await self._obtener_por_clave(
            self.TABLA, self.CLAVE_PRIMARIA, str(ruta), esquema
        )

    async def obtener_por_rol(self, rol, esquema=None):
        """Obtiene las rutas asignadas a un rol especifico."""
        return await self._obtener_por_clave(
            self.TABLA, "rol", str(rol), esquema
        )

    async def crear(self, datos, esquema=None):
        """Crea una nueva asignacion de ruta a rol."""
        return await self._crear(self.TABLA, datos, esquema)

    async def eliminar(self, ruta, esquema=None):
        """Elimina asignaciones de ruta a rol por ruta."""
        return await self._eliminar(
            self.TABLA, self.CLAVE_PRIMARIA, str(ruta), esquema
        )
