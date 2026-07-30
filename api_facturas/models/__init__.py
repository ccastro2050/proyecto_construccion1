"""Paquete de modelos Pydantic — uno por cada tabla de la BD."""
 
from .persona import Persona
from .empresa import Empresa
from .cliente import Cliente
from .vendedor import Vendedor
from .producto import Producto
from .factura import Factura
from .productosporfactura import ProductosPorFactura
from .usuario import Usuario
from .rol import Rol
from .rol_usuario import RolUsuario
from .ruta import Ruta
from .rutarol import RutaRol
 
# Diccionario: nombre de tabla → clase del modelo Pydantic
MODELOS_POR_TABLA = {
    "persona": Persona,
    "empresa": Empresa,
    "cliente": Cliente,
    "vendedor": Vendedor,
    "producto": Producto,
    "factura": Factura,
    "productosporfactura": ProductosPorFactura,
    "usuario": Usuario,
    "rol": Rol,
    "rol_usuario": RolUsuario,
    "ruta": Ruta,
    "rutarol": RutaRol,
}
 
__all__ = [
    "Persona", "Empresa", "Cliente", "Vendedor",
    "Producto", "Factura", "ProductosPorFactura",
    "Usuario", "Rol", "RolUsuario", "Ruta", "RutaRol",
    "MODELOS_POR_TABLA",
]
