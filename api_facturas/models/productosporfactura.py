"""Modelo Pydantic para la tabla productosporfactura."""
 
from pydantic import BaseModel
 
 
class ProductosPorFactura(BaseModel):
    """Representa una línea de detalle de factura."""
    fknumfactura: int              # PK compuesta (parte 1) + FK
    fkcodproducto: str             # PK compuesta (parte 2) + FK
    cantidad: int
    subtotal: float | None = None
