"""Repositorio de usuario para PostgreSQL."""

from repositorios.base_repositorio_postgresql import BaseRepositorioPostgreSQL


class RepositorioUsuarioPostgreSQL(BaseRepositorioPostgreSQL):
    """Acceso a datos de usuario en PostgreSQL."""

    TABLA = "usuario"
    CLAVE_PRIMARIA = "email"
    CAMPOS_ENCRIPTAR = "contrasena"

    async def obtener_todos(self, esquema=None, limite=None):
        """Obtiene todos los usuarios."""
        return await self._obtener_filas(self.TABLA, esquema, limite)

    async def obtener_por_email(self, email, esquema=None):
        """Obtiene un usuario por su email."""
        return await self._obtener_por_clave(
            self.TABLA, self.CLAVE_PRIMARIA, str(email), esquema
        )

    async def crear(self, datos, esquema=None):
        """Crea un nuevo usuario con contrasena encriptada."""
        return await self._crear(
            self.TABLA, datos, esquema, self.CAMPOS_ENCRIPTAR
        )

    async def actualizar(self, email, datos, esquema=None):
        """Actualiza un usuario existente con contrasena encriptada."""
        return await self._actualizar(
            self.TABLA, self.CLAVE_PRIMARIA, str(email), datos, esquema,
            self.CAMPOS_ENCRIPTAR
        )

    async def eliminar(self, email, esquema=None):
        """Elimina un usuario por su email."""
        return await self._eliminar(
            self.TABLA, self.CLAVE_PRIMARIA, str(email), esquema
        )

    async def obtener_hash_contrasena(self, email, esquema=None):
        """Obtiene el hash de la contrasena de un usuario por su email."""
        return await self._obtener_hash_contrasena(
            self.TABLA, "email", "contrasena", email, esquema
        )
