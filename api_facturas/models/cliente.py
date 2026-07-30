"""Modelo Pydantic para la tabla cliente."""
 
from pydantic import BaseModel
 
 
class Cliente(BaseModel):
    """Representa un cliente en la base de datos."""
    id: int | None = None          # serial (autoincremental), no se envía al crear
    credito: float | None = None
    fkcodpersona: str
    fkcodempresa: str
