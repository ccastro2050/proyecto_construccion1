"""Modelo Pydantic para la tabla empresa."""
 
from pydantic import BaseModel
 
 
class Empresa(BaseModel):
    """Representa una empresa en la base de datos."""
    codigo: str
    nombre: str
