from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing import Annotated, Optional
from models.estanteria import Estanteria

class Bodega(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")  # Alias directo de _id
    ciudad: Annotated[str, StringConstraints(min_length=3, max_length=50)]
    direccion: Annotated[str, StringConstraints(min_length=5, max_length=100)]
    estanterias: list[Estanteria] = []

    def __str__(self):
        return f"{self.ciudad} - {self.direccion}"

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "ciudad": "Bogotá",
                "direccion": "Calle 2"
            }
        }
    )