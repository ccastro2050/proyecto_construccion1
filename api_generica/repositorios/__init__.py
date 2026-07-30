"""Paquete de repositorios — Implementaciones de acceso a datos."""

from .repositorio_lectura_sqlserver import RepositorioLecturaSqlServer
from .repositorio_lectura_postgresql import RepositorioLecturaPostgreSQL
from .repositorio_lectura_mysql_mariadb import RepositorioLecturaMysqlMariaDB

__all__ = [
    "RepositorioLecturaSqlServer",
    "RepositorioLecturaPostgreSQL",
    "RepositorioLecturaMysqlMariaDB",
]
