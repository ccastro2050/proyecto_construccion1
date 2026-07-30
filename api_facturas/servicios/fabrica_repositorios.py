"""
fabrica_repositorios.py — Factory centralizada.

Lee DB_PROVIDER del .env y crea el repositorio y servicio correspondientes.
Incluye factories genérica (retrocompatibilidad) y específicas por entidad.
"""

from servicios.conexion.proveedor_conexion import ProveedorConexion
from servicios.servicio_crud import ServicioCrud

# ── Imports de repositorios base (retrocompatibilidad) ────────────────
from repositorios import (
    RepositorioLecturaSqlServer,
    RepositorioLecturaPostgreSQL,
    RepositorioLecturaMysqlMariaDB,
)

# ── Imports de repositorios específicos ───────────────────────────────
from repositorios.persona import (
    RepositorioPersonaPostgreSQL, RepositorioPersonaSqlServer,
    RepositorioPersonaMysqlMariaDB,
)
from repositorios.empresa import (
    RepositorioEmpresaPostgreSQL, RepositorioEmpresaSqlServer,
    RepositorioEmpresaMysqlMariaDB,
)
from repositorios.cliente import (
    RepositorioClientePostgreSQL, RepositorioClienteSqlServer,
    RepositorioClienteMysqlMariaDB,
)
from repositorios.vendedor import (
    RepositorioVendedorPostgreSQL, RepositorioVendedorSqlServer,
    RepositorioVendedorMysqlMariaDB,
)
from repositorios.producto import (
    RepositorioProductoPostgreSQL, RepositorioProductoSqlServer,
    RepositorioProductoMysqlMariaDB,
)
from repositorios.factura import (
    RepositorioFacturaPostgreSQL, RepositorioFacturaSqlServer,
    RepositorioFacturaMysqlMariaDB,
)
from repositorios.productosporfactura import (
    RepositorioProductosPorFacturaPostgreSQL,
    RepositorioProductosPorFacturaSqlServer,
    RepositorioProductosPorFacturaMysqlMariaDB,
)
from repositorios.usuario import (
    RepositorioUsuarioPostgreSQL, RepositorioUsuarioSqlServer,
    RepositorioUsuarioMysqlMariaDB,
)
from repositorios.rol import (
    RepositorioRolPostgreSQL, RepositorioRolSqlServer,
    RepositorioRolMysqlMariaDB,
)
from repositorios.rol_usuario import (
    RepositorioRolUsuarioPostgreSQL, RepositorioRolUsuarioSqlServer,
    RepositorioRolUsuarioMysqlMariaDB,
)
from repositorios.ruta import (
    RepositorioRutaPostgreSQL, RepositorioRutaSqlServer,
    RepositorioRutaMysqlMariaDB,
)
from repositorios.rutarol import (
    RepositorioRutaRolPostgreSQL, RepositorioRutaRolSqlServer,
    RepositorioRutaRolMysqlMariaDB,
)

# ── Imports de servicios específicos ──────────────────────────────────
from servicios.servicio_persona import ServicioPersona
from servicios.servicio_empresa import ServicioEmpresa
from servicios.servicio_cliente import ServicioCliente
from servicios.servicio_vendedor import ServicioVendedor
from servicios.servicio_producto import ServicioProducto
from servicios.servicio_factura import ServicioFactura
from servicios.servicio_productosporfactura import ServicioProductosPorFactura
from servicios.servicio_usuario import ServicioUsuario
from servicios.servicio_rol import ServicioRol
from servicios.servicio_rol_usuario import ServicioRolUsuario
from servicios.servicio_ruta import ServicioRuta
from servicios.servicio_rutarol import ServicioRutaRol


# =====================================================================
# FACTORY GENÉRICA (retrocompatibilidad con entidades_controller.py)
# =====================================================================

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
    """Crea el repositorio genérico según DB_PROVIDER en .env."""
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
    """Crea el servicio CRUD genérico (para entidades_controller.py)."""
    repositorio = crear_repositorio_lectura()
    return ServicioCrud(repositorio_lectura=repositorio)


# =====================================================================
# FACTORIES ESPECÍFICAS POR ENTIDAD
# =====================================================================

def _obtener_proveedor():
    """Obtiene el proveedor de conexión y su nombre."""
    proveedor = ProveedorConexion()
    return proveedor, proveedor.proveedor_actual


def _crear_repo_entidad(repos_por_proveedor: dict, proveedor, nombre: str):
    """Instancia el repositorio específico según el proveedor activo."""
    clase = repos_por_proveedor.get(nombre)
    if clase is None:
        raise ValueError(
            f"Proveedor '{nombre}' no soportado para esta entidad. "
            f"Opciones: {list(repos_por_proveedor.keys())}"
        )
    return clase(proveedor)


# ── Persona ───────────────────────────────────────────────────────────
_REPOS_PERSONA = {
    "sqlserver": RepositorioPersonaSqlServer,
    "sqlserverexpress": RepositorioPersonaSqlServer,
    "localdb": RepositorioPersonaSqlServer,
    "postgres": RepositorioPersonaPostgreSQL,
    "postgresql": RepositorioPersonaPostgreSQL,
    "mysql": RepositorioPersonaMysqlMariaDB,
    "mariadb": RepositorioPersonaMysqlMariaDB,
}

def crear_servicio_persona() -> ServicioPersona:
    """Crea el servicio específico de persona."""
    proveedor, nombre = _obtener_proveedor()
    repo = _crear_repo_entidad(_REPOS_PERSONA, proveedor, nombre)
    return ServicioPersona(repo)


# ── Empresa ───────────────────────────────────────────────────────────
_REPOS_EMPRESA = {
    "sqlserver": RepositorioEmpresaSqlServer,
    "sqlserverexpress": RepositorioEmpresaSqlServer,
    "localdb": RepositorioEmpresaSqlServer,
    "postgres": RepositorioEmpresaPostgreSQL,
    "postgresql": RepositorioEmpresaPostgreSQL,
    "mysql": RepositorioEmpresaMysqlMariaDB,
    "mariadb": RepositorioEmpresaMysqlMariaDB,
}

def crear_servicio_empresa() -> ServicioEmpresa:
    """Crea el servicio específico de empresa."""
    proveedor, nombre = _obtener_proveedor()
    repo = _crear_repo_entidad(_REPOS_EMPRESA, proveedor, nombre)
    return ServicioEmpresa(repo)


# ── Cliente ───────────────────────────────────────────────────────────
_REPOS_CLIENTE = {
    "sqlserver": RepositorioClienteSqlServer,
    "sqlserverexpress": RepositorioClienteSqlServer,
    "localdb": RepositorioClienteSqlServer,
    "postgres": RepositorioClientePostgreSQL,
    "postgresql": RepositorioClientePostgreSQL,
    "mysql": RepositorioClienteMysqlMariaDB,
    "mariadb": RepositorioClienteMysqlMariaDB,
}

def crear_servicio_cliente() -> ServicioCliente:
    """Crea el servicio específico de cliente."""
    proveedor, nombre = _obtener_proveedor()
    repo = _crear_repo_entidad(_REPOS_CLIENTE, proveedor, nombre)
    return ServicioCliente(repo)


# ── Vendedor ──────────────────────────────────────────────────────────
_REPOS_VENDEDOR = {
    "sqlserver": RepositorioVendedorSqlServer,
    "sqlserverexpress": RepositorioVendedorSqlServer,
    "localdb": RepositorioVendedorSqlServer,
    "postgres": RepositorioVendedorPostgreSQL,
    "postgresql": RepositorioVendedorPostgreSQL,
    "mysql": RepositorioVendedorMysqlMariaDB,
    "mariadb": RepositorioVendedorMysqlMariaDB,
}

def crear_servicio_vendedor() -> ServicioVendedor:
    """Crea el servicio específico de vendedor."""
    proveedor, nombre = _obtener_proveedor()
    repo = _crear_repo_entidad(_REPOS_VENDEDOR, proveedor, nombre)
    return ServicioVendedor(repo)


# ── Producto ──────────────────────────────────────────────────────────
_REPOS_PRODUCTO = {
    "sqlserver": RepositorioProductoSqlServer,
    "sqlserverexpress": RepositorioProductoSqlServer,
    "localdb": RepositorioProductoSqlServer,
    "postgres": RepositorioProductoPostgreSQL,
    "postgresql": RepositorioProductoPostgreSQL,
    "mysql": RepositorioProductoMysqlMariaDB,
    "mariadb": RepositorioProductoMysqlMariaDB,
}

def crear_servicio_producto() -> ServicioProducto:
    """Crea el servicio específico de producto."""
    proveedor, nombre = _obtener_proveedor()
    repo = _crear_repo_entidad(_REPOS_PRODUCTO, proveedor, nombre)
    return ServicioProducto(repo)


# ── Factura ───────────────────────────────────────────────────────────
_REPOS_FACTURA = {
    "sqlserver": RepositorioFacturaSqlServer,
    "sqlserverexpress": RepositorioFacturaSqlServer,
    "localdb": RepositorioFacturaSqlServer,
    "postgres": RepositorioFacturaPostgreSQL,
    "postgresql": RepositorioFacturaPostgreSQL,
    "mysql": RepositorioFacturaMysqlMariaDB,
    "mariadb": RepositorioFacturaMysqlMariaDB,
}

def crear_servicio_factura() -> ServicioFactura:
    """Crea el servicio específico de factura."""
    proveedor, nombre = _obtener_proveedor()
    repo = _crear_repo_entidad(_REPOS_FACTURA, proveedor, nombre)
    return ServicioFactura(repo)


# ── ProductosPorFactura ──────────────────────────────────────────────
_REPOS_PRODUCTOSPORFACTURA = {
    "sqlserver": RepositorioProductosPorFacturaSqlServer,
    "sqlserverexpress": RepositorioProductosPorFacturaSqlServer,
    "localdb": RepositorioProductosPorFacturaSqlServer,
    "postgres": RepositorioProductosPorFacturaPostgreSQL,
    "postgresql": RepositorioProductosPorFacturaPostgreSQL,
    "mysql": RepositorioProductosPorFacturaMysqlMariaDB,
    "mariadb": RepositorioProductosPorFacturaMysqlMariaDB,
}

def crear_servicio_productosporfactura() -> ServicioProductosPorFactura:
    """Crea el servicio específico de productos por factura."""
    proveedor, nombre = _obtener_proveedor()
    repo = _crear_repo_entidad(_REPOS_PRODUCTOSPORFACTURA, proveedor, nombre)
    return ServicioProductosPorFactura(repo)


# ── Usuario ──────────────────────────────────────────────────────────
_REPOS_USUARIO = {
    "sqlserver": RepositorioUsuarioSqlServer,
    "sqlserverexpress": RepositorioUsuarioSqlServer,
    "localdb": RepositorioUsuarioSqlServer,
    "postgres": RepositorioUsuarioPostgreSQL,
    "postgresql": RepositorioUsuarioPostgreSQL,
    "mysql": RepositorioUsuarioMysqlMariaDB,
    "mariadb": RepositorioUsuarioMysqlMariaDB,
}

def crear_servicio_usuario() -> ServicioUsuario:
    """Crea el servicio específico de usuario."""
    proveedor, nombre = _obtener_proveedor()
    repo = _crear_repo_entidad(_REPOS_USUARIO, proveedor, nombre)
    return ServicioUsuario(repo)


# ── Rol ──────────────────────────────────────────────────────────────
_REPOS_ROL = {
    "sqlserver": RepositorioRolSqlServer,
    "sqlserverexpress": RepositorioRolSqlServer,
    "localdb": RepositorioRolSqlServer,
    "postgres": RepositorioRolPostgreSQL,
    "postgresql": RepositorioRolPostgreSQL,
    "mysql": RepositorioRolMysqlMariaDB,
    "mariadb": RepositorioRolMysqlMariaDB,
}

def crear_servicio_rol() -> ServicioRol:
    """Crea el servicio específico de rol."""
    proveedor, nombre = _obtener_proveedor()
    repo = _crear_repo_entidad(_REPOS_ROL, proveedor, nombre)
    return ServicioRol(repo)


# ── RolUsuario ───────────────────────────────────────────────────────
_REPOS_ROL_USUARIO = {
    "sqlserver": RepositorioRolUsuarioSqlServer,
    "sqlserverexpress": RepositorioRolUsuarioSqlServer,
    "localdb": RepositorioRolUsuarioSqlServer,
    "postgres": RepositorioRolUsuarioPostgreSQL,
    "postgresql": RepositorioRolUsuarioPostgreSQL,
    "mysql": RepositorioRolUsuarioMysqlMariaDB,
    "mariadb": RepositorioRolUsuarioMysqlMariaDB,
}

def crear_servicio_rol_usuario() -> ServicioRolUsuario:
    """Crea el servicio específico de rol-usuario."""
    proveedor, nombre = _obtener_proveedor()
    repo = _crear_repo_entidad(_REPOS_ROL_USUARIO, proveedor, nombre)
    return ServicioRolUsuario(repo)


# ── Ruta ─────────────────────────────────────────────────────────────
_REPOS_RUTA = {
    "sqlserver": RepositorioRutaSqlServer,
    "sqlserverexpress": RepositorioRutaSqlServer,
    "localdb": RepositorioRutaSqlServer,
    "postgres": RepositorioRutaPostgreSQL,
    "postgresql": RepositorioRutaPostgreSQL,
    "mysql": RepositorioRutaMysqlMariaDB,
    "mariadb": RepositorioRutaMysqlMariaDB,
}

def crear_servicio_ruta() -> ServicioRuta:
    """Crea el servicio específico de ruta."""
    proveedor, nombre = _obtener_proveedor()
    repo = _crear_repo_entidad(_REPOS_RUTA, proveedor, nombre)
    return ServicioRuta(repo)


# ── RutaRol ──────────────────────────────────────────────────────────
_REPOS_RUTAROL = {
    "sqlserver": RepositorioRutaRolSqlServer,
    "sqlserverexpress": RepositorioRutaRolSqlServer,
    "localdb": RepositorioRutaRolSqlServer,
    "postgres": RepositorioRutaRolPostgreSQL,
    "postgresql": RepositorioRutaRolPostgreSQL,
    "mysql": RepositorioRutaRolMysqlMariaDB,
    "mariadb": RepositorioRutaRolMysqlMariaDB,
}

def crear_servicio_rutarol() -> ServicioRutaRol:
    """Crea el servicio específico de ruta-rol."""
    proveedor, nombre = _obtener_proveedor()
    repo = _crear_repo_entidad(_REPOS_RUTAROL, proveedor, nombre)
    return ServicioRutaRol(repo)
