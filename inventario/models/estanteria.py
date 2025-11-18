from pydantic import BaseModel, StringConstraints
from typing import Annotated, Optional
from models.item import Item
from models.producto import Item

class Estanteria(BaseModel):
    area_bodega: Annotated[str, StringConstraints(min_length=3, max_length=100)]
    numero_estanteria: Annotated[str, StringConstraints(min_length=1, max_length=10)]
    items_disponibles: Optional[list[Item]] = []