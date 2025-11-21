from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Literal
from models.movimiento import MovimientoReciente

class Item(BaseModel):
    sku: str = Field(alias="_id")
    ingreso_fecha: datetime
    salida_fecha: Optional[datetime] = None
    estado: Literal["disponible", "vendido", "devuelto", "dañado"]
    atributos: Optional[dict] = None
    producto_id: str
    estanteria_id: str
    bodega_id: str

    movimientos_recientes: List[MovimientoReciente] = []

    model_config = ConfigDict(populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "ITEM123456",
                "ingreso_fecha": "2024-01-15T10:00:00Z",
                "estado": "disponible",
                "producto_id": "PROD001",
                "estanteria_id": "EST323",
                "bodega_id": "BOD1",
                "atributos": {
                    "color": "rojo",
                    "talla": "M"
                }
            }
        }
    )
