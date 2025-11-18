from pydantic import BaseModel, ConfigDict, StringConstraints
from typing import Annotated, Optional
from models.item import Item


class Producto(BaseModel):
    codigo_barras: Annotated[str, StringConstraints(min_length=3, max_length=20)]
    nombre: Annotated[str, StringConstraints(min_length=2, max_length=100)]
    descripcion: Annotated[str, StringConstraints(min_length=5, max_length=300)]
    precio: float
    cantidad: Optional[int] = None
    items_disponibles: Optional[list[Item]] = None # Items que estan disponibles en inventario
    items: Optional[list[Item]] = None # Todos los items asociados/ han sido asociados al producto

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "codigo_barras": "1234567890123",
                "nombre": "Camiseta",
                "descripcion": "Camiseta de algodón, manga corta",
                "precio": 19.99,
                "cantidad": 10
            }
        }
    )

class Camisa(Producto):
    talla: Annotated[str, StringConstraints(min_length=1, max_length=5)]
    color: Annotated[str, StringConstraints(min_length=3, max_length=30)]

class Pantalon(Producto):
    talla: Annotated[str, StringConstraints(min_length=1, max_length=5)]
    tipo: Annotated[str, StringConstraints(min_length=3, max_length=50)]

class Zapato(Producto):
    talla: float
    material: Annotated[str, StringConstraints(min_length=3, max_length=50)]

class Gafas(Producto):
    tipo: Annotated[str, StringConstraints(min_length=3, max_length=50)]
    proteccion_uv: bool