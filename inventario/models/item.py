from pydantic import BaseModel, StringConstraints
from datetime import datetime
from typing import Annotated, Literal, Optional

class Item(BaseModel):
    sku: Annotated[str, StringConstraints(min_length=3, max_length=20)]
    ingreso_fecha: datetime
    salida_fecha: Optional[datetime] = None
    estado: Annotated[str, Literal["disponible", "vendido", "devuelto", "dañado"]] = "disponible"
    producto_id: Optional[str] = None
    estanteria_id: Optional[str] = None
    bodega_id: Optional[str] = None