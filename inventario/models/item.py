from pydantic import BaseModel, StringConstraints
from datetime import datetime
from typing import Annotated, Literal, Optional

class Item(BaseModel):
    sku: Annotated[str, StringConstraints(min_length=3, max_length=20)]
    ingreso_fecha: datetime
    salida_fecha: Optional[datetime] = None
    estado: Annotated[str, Literal["disponible", "vendido", "devuelto", "dañado"]] = "disponible"
    producto_id: str 
    estanteria_id: str 
    bodega_id: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "sku": "ITEM123456",
                "ingreso_fecha": "2024-01-15T10:00:00Z",
                "salida_fecha": None,
                "estado": "disponible",
                "producto_id": "PROD123456",
                "estanteria_id": "EST123",
                "bodega_id": "BOD123"
            }
        }
    }