"""
repositorio_lectura_generico.py — Adaptadores públicos del CRUD genérico.

Cierra el problema conocido documentado en docs/spec_kit/4_research.md:
`ServicioCrud` (entidades_controller.py) llama los métodos PÚBLICOS del
contrato `IRepositorioLecturaTabla` (`obtener_filas`, `crear`, ...), pero
las clases base solo exponían los métodos protegidos (`_obtener_filas`,
`_crear`, ...). Estas subclases delegan uno a uno, sin tocar las bases
ni los repositorios específicos por entidad (que siguen heredando de las
bases directamente).
"""

from repositorios.base_repositorio_postgresql import BaseRepositorioPostgreSQL
from repositorios.base_repositorio_sqlserver import BaseRepositorioSqlServer
from repositorios.base_repositorio_mysql_mariadb import BaseRepositorioMysqlMariaDB


class _MezclaLecturaGenerica:
    """Expone el contrato público delegando en los métodos protegidos."""

    async def obtener_filas(self, nombre_tabla, esquema=None, limite=None):
        return await self._obtener_filas(nombre_tabla, esquema, limite)

    async def obtener_por_clave(self, nombre_tabla, nombre_clave, valor,
                                esquema=None):
        return await self._obtener_por_clave(
            nombre_tabla, nombre_clave, valor, esquema
        )

    async def crear(self, nombre_tabla, datos, esquema=None,
                    campos_encriptar=None):
        return await self._crear(
            nombre_tabla, datos, esquema, campos_encriptar
        )

    async def actualizar(self, nombre_tabla, nombre_clave, valor_clave,
                         datos, esquema=None, campos_encriptar=None):
        return await self._actualizar(
            nombre_tabla, nombre_clave, valor_clave, datos,
            esquema, campos_encriptar
        )

    async def eliminar(self, nombre_tabla, nombre_clave, valor_clave,
                       esquema=None):
        return await self._eliminar(
            nombre_tabla, nombre_clave, valor_clave, esquema
        )

    async def obtener_hash_contrasena(self, nombre_tabla, campo_usuario,
                                      campo_contrasena, valor_usuario,
                                      esquema=None):
        return await self._obtener_hash_contrasena(
            nombre_tabla, campo_usuario, campo_contrasena,
            valor_usuario, esquema
        )


class RepositorioLecturaPostgreSQL(_MezclaLecturaGenerica,
                                   BaseRepositorioPostgreSQL):
    """CRUD genérico sobre PostgreSQL (contrato IRepositorioLecturaTabla)."""


class RepositorioLecturaSqlServer(_MezclaLecturaGenerica,
                                  BaseRepositorioSqlServer):
    """CRUD genérico sobre SQL Server (contrato IRepositorioLecturaTabla)."""


class RepositorioLecturaMysqlMariaDB(_MezclaLecturaGenerica,
                                     BaseRepositorioMysqlMariaDB):
    """CRUD genérico sobre MySQL/MariaDB (contrato IRepositorioLecturaTabla)."""
