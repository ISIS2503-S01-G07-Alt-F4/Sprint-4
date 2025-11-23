from pydantic import BaseModel, Field, StringConstraints, ConfigDict
from typing import Annotated, Literal, Dict, Any, Optional
from datetime import datetime


class AuditEvent(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now()) 
    user_id: str
    audited_service_id: str
    action: Literal["CREATE", "READ", "UPDATE", "DELETE", "LOGIN", "LOGOUT"]
    description: Annotated[str, StringConstraints(min_length=3, max_length=300)]
    entity: str
    entity_id: str
    metadata: Dict[str, Any] | None = None #Datos sobre la acción que se realizó
    ip: str | None = None
    
    def __str__(self) -> str:
        return (f"AuditEvent(timestamp={self.timestamp}, user_id={self.user_id}, "
                f"audit_service_id={self.audit_service_id}, action={self.action}, "
                f"description={self.description}, entity={self.entity}, "
                f"entity_id={self.entity_id}, metadata={self.metadata}, ip={self.ip})")
    
    model_config = ConfigDict(populate_by_name=True,
        json_schema_extra={
            "example": {
                "timestamp": "2025-11-22 21:01:08.923508",
                "user_id": "123",
                "audited_service_id": "2",
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
    
class AuditLog(AuditEvent):
    id: Optional[str] = Field(default=None, alias="_id")  # Alias directo de _id
    registered_at: datetime = Field(default_factory=datetime.now())