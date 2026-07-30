"""Modelo Pydantic para la tabla rol."""
 
from pydantic import BaseModel
 
 
class Rol(BaseModel):
    """Representa un rol en la base de datos."""
    id: int | None = None          # serial (autoincremental)
    nombre: str
