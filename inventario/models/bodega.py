from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing import Annotated, Optional
from models.estanteria import Estanteria
class Bodega(BaseModel):
    ciudad: Annotated[str,StringConstraints(min_length=3, max_length=50)]
    direccion: Annotated[str,StringConstraints(min_length=5, max_length=100)]
    estanterias: list[Estanteria] = []
    
    def __str__(self):
        return f"{self.ciudad} - {self.direccion}"
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ciudad": "Madrid",
                "direccion": "Calle Falsa 123"
            }
        }
    )