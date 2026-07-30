"""Modelo Pydantic para la tabla factura."""
 
from pydantic import BaseModel
 
 
class Factura(BaseModel):
    """Representa una factura en la base de datos."""
    numero: int | None = None      # serial (autoincremental)
    fecha: str | None = None       # timestamp, se envía como texto ISO
    total: float | None = None
    fkidcliente: int
    fkidvendedor: int
