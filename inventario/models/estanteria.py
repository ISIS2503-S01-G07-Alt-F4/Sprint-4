from pydantic import BaseModel, StringConstraints, Field
from typing import Annotated, Optional
from models.item import Item
from models.producto import Item

class Estanteria(BaseModel):
    numero_estanteria: str = Field(alias="_id")
    area_bodega: Annotated[str, StringConstraints(min_length=3, max_length=100)]