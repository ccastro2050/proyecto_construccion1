"""
fabrica_repositorios.py — Factory centralizada.

Lee DB_PROVIDER del .env y crea el repositorio y servicio correspondientes.
Agregar un nuevo proveedor = agregar 1 línea al diccionario.
"""

from servicios.conexion.proveedor_conexion import ProveedorConexion
from servicios.servicio_crud import ServicioCrud

from repositorios import (
    RepositorioLecturaSqlServer,
    RepositorioLecturaPostgreSQL,
    RepositorioLecturaMysqlMariaDB,
)

# Diccionario: proveedor → clase del repositorio
_REPOSITORIOS_LECTURA = {
    "sqlserver": RepositorioLecturaSqlServer,
    "sqlserverexpress": RepositorioLecturaSqlServer,
    "localdb": RepositorioLecturaSqlServer,
    "postgres": RepositorioLecturaPostgreSQL,
    "postgresql": RepositorioLecturaPostgreSQL,
    "mysql": RepositorioLecturaMysqlMariaDB,
    "mariadb": RepositorioLecturaMysqlMariaDB,
}


def crear_repositorio_lectura():
    """Crea el repositorio correcto según DB_PROVIDER en .env."""
    proveedor = ProveedorConexion()
    nombre = proveedor.proveedor_actual

    clase_repositorio = _REPOSITORIOS_LECTURA.get(nombre)
    if clase_repositorio is None:
        raise ValueError(
            f"Proveedor '{nombre}' no tiene repositorio registrado. "
            f"Opciones: {list(_REPOSITORIOS_LECTURA.keys())}"
        )

    return clase_repositorio(proveedor)


def crear_servicio_crud() -> ServicioCrud:
    """Crea el servicio CRUD con el repositorio del proveedor activo."""
    repositorio = crear_repositorio_lectura()
    return ServicioCrud(repositorio_lectura=repositorio)
