"""Modelo Pydantic para la tabla rutarol."""
 
from pydantic import BaseModel
 
 
class RutaRol(BaseModel):
    """Representa la relación ruta-rol."""
    ruta: str                      # PK compuesta + FK → ruta.ruta
    rol: str                       # PK compuesta + FK
