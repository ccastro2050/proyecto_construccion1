"""Modelo Pydantic para la tabla persona."""
 
from pydantic import BaseModel
 
 
class Persona(BaseModel):
    """Representa una persona en la base de datos."""
    codigo: str
    nombre: str
    email: str | None = None
    telefono: str | None = None
