"""Paquete de repositorios — Clases base e implementaciones específicas."""

from .base_repositorio_postgresql import BaseRepositorioPostgreSQL
from .base_repositorio_sqlserver import BaseRepositorioSqlServer
from .base_repositorio_mysql_mariadb import BaseRepositorioMysqlMariaDB

# Aliases de retrocompatibilidad para el controller genérico
RepositorioLecturaPostgreSQL = BaseRepositorioPostgreSQL
RepositorioLecturaSqlServer = BaseRepositorioSqlServer
RepositorioLecturaMysqlMariaDB = BaseRepositorioMysqlMariaDB

__all__ = [
    "BaseRepositorioPostgreSQL",
    "BaseRepositorioSqlServer",
    "BaseRepositorioMysqlMariaDB",
    "RepositorioLecturaPostgreSQL",
    "RepositorioLecturaSqlServer",
    "RepositorioLecturaMysqlMariaDB",
]
