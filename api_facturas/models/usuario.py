"""Modelo Pydantic para la tabla usuario."""
 
from pydantic import BaseModel
 
 
class Usuario(BaseModel):
    """Representa un usuario en la base de datos."""
    email: str                     # PK
    contrasena: str                # se encripta con BCrypt antes de guardar
