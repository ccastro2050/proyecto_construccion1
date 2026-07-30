"""Modelo Pydantic para la tabla ruta."""
 
from pydantic import BaseModel
 
 
class Ruta(BaseModel):
    """Representa una ruta de la aplicación."""
    ruta: str                      # PK
    descripcion: str | None = None
