from pydantic import BaseModel, ConfigDict, StringConstraints, Field
from typing import Annotated, Optional
from models.item import Item


class Producto(BaseModel):
    codigo_barras: str = Field(alias="_id")
    tipo: str 
    nombre: Annotated[str, StringConstraints(min_length=2, max_length=100)]
    descripcion: Annotated[str, StringConstraints(min_length=5, max_length=300)]
    precio: float
    cantidad_items_disponibles: int = 0
    atributos: dict = {}
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "codigo_barras": "1234567890123",
                "tipo": "Ropa",
                "nombre": "Camiseta",
                "descripcion": "Camiseta de algodón, manga corta",
                "precio": 19.99,
            }
        },
        populate_by_name=True
    )

        
