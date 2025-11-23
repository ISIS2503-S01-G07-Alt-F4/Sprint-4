from pydantic import BaseModel, Field, StringConstraints, ConfigDict
from typing import Annotated, Literal, Dict, Any
from datetime import datetime


class AuditEvent(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now())
    user_id: str
    audit_service_id: str
    action: Literal["CREATE", "READ", "UPDATE", "DELETE", "LOGIN", "LOGOUT"]
    description: Annotated[str, StringConstraints(min_length=3, max_length=300)]
    entity: str
    entity_id: str
    metadata: Dict[str, Any] | None = None #Datos sobre la acción que se realizó
    ip: str | None = None
    
    model_config = ConfigDict(populate_by_name=True,
        json_schema_extra={
            "example": {
                "timestamp": "2025-11-22 21:01:08.923508",
                "user_id": "123",
                "audit_service_id": "2",
                "action": "CREATE",
                "description": "Se ha creado un producto",
                "entity": "PRODUCT",
                "entity_id": "14",
                "metadata": {
                    "new": {
                        "codigo_barras": "1234567890123",
                        "tipo": "Ropa",
                        "nombre": "Camiseta",
                        "descripcion": "Camiseta de algodón, manga corta",
                        "precio": 19.99,
                    }
                },
                "ip": "127.168.1.1"
            }
        }
    )