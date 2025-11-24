from pydantic import BaseModel, Field, StringConstraints
from datetime import datetime
from typing import Annotated, Literal, Optional

class Movimiento(BaseModel):
    tipo: Literal["ingreso", "ubicacion", "estado", "salida"]
    fecha: datetime
    descripcion: Annotated[str, StringConstraints(min_length=3, max_length=300)]
    usuario_id: str

class MovimientoReciente(Movimiento):
    """
    Modelo ligero para embeber dentro del Item.
    Solo contiene información esencial del movimiento.
    """
    pass

class MovimientoHistorico(Movimiento):
    sku: str = Field(alias="_id")         # SKU
    bodega_id: Optional[str] = None
    estanteria_id: Optional[str] = None
