"""Paquete de repositorios — Clases base e implementaciones específicas."""

from .base_repositorio_postgresql import BaseRepositorioPostgreSQL
from .base_repositorio_sqlserver import BaseRepositorioSqlServer
from .base_repositorio_mysql_mariadb import BaseRepositorioMysqlMariaDB

# Repositorios del CRUD genérico (entidades_controller.py): exponen el
# contrato público IRepositorioLecturaTabla delegando en las bases.
from .repositorio_lectura_generico import (
    RepositorioLecturaPostgreSQL,
    RepositorioLecturaSqlServer,
    RepositorioLecturaMysqlMariaDB,
)

__all__ = [
    "BaseRepositorioPostgreSQL",
    "BaseRepositorioSqlServer",
    "BaseRepositorioMysqlMariaDB",
    "RepositorioLecturaPostgreSQL",
    "RepositorioLecturaSqlServer",
    "RepositorioLecturaMysqlMariaDB",
]
