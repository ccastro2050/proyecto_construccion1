"""Repositorio de rol_usuario para SQL Server."""

from repositorios.base_repositorio_sqlserver import BaseRepositorioSqlServer


class RepositorioRolUsuarioSqlServer(BaseRepositorioSqlServer):
    """Acceso a datos de rol_usuario en SQL Server."""

    TABLA = "rol_usuario"
    CLAVE_PRIMARIA = "fkemail"

    async def obtener_todos(self, esquema=None, limite=None):
        """Obtiene todos los roles de usuario."""
        return await self._obtener_filas(self.TABLA, esquema, limite)

    async def obtener_por_email(self, fkemail, esquema=None):
        """Obtiene los roles de un usuario por su email."""
        return await self._obtener_por_clave(
            self.TABLA, "fkemail", str(fkemail), esquema
        )

    async def obtener_por_rol(self, fkidrol, esquema=None):
        """Obtiene los usuarios que tienen un rol especifico."""
        return await self._obtener_por_clave(
            self.TABLA, "fkidrol", str(fkidrol), esquema
        )

    async def crear(self, datos, esquema=None):
        """Crea una nueva asignacion de rol a usuario."""
        return await self._crear(self.TABLA, datos, esquema)

    async def eliminar(self, fkemail, esquema=None):
        """Elimina asignaciones de rol por email de usuario."""
        return await self._eliminar(
            self.TABLA, self.CLAVE_PRIMARIA, str(fkemail), esquema
        )
