"""Modelo Pydantic para la tabla vendedor."""
 
from pydantic import BaseModel
 
 
class Vendedor(BaseModel):
    """Representa un vendedor en la base de datos."""
    id: int | None = None          # serial (autoincremental)
    carnet: int | None = None
    direccion: str | None = None
    fkcodpersona: str
