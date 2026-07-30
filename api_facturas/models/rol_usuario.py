"""Modelo Pydantic para la tabla rol_usuario."""
 
from pydantic import BaseModel
 
 
class RolUsuario(BaseModel):
    """Representa la relación rol-usuario."""
    fkemail: str                   # PK compuesta + FK → usuario.email
    fkidrol: int                   # PK compuesta + FK → rol.id
