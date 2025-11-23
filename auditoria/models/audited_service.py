from pydantic import BaseModel, StringConstraints, ConfigDict
from typing import Annotated, List, Optional
from models.audit_event import AuditLog

class Service(BaseModel):
    name: Annotated[str, StringConstraints(min_length=2, max_length=100)]
    
    model_config = ConfigDict(populate_by_name=True,
        json_schema_extra={
            "example": {
                "name": "Servicio de Gestión de Usuarios"
            }
        }
    )
    
    def __str__(self) -> str:
        return f"{self.name}"
    
class AuditedService(Service):
    id : Optional[str] = None
    recent_logs: List[AuditLog] = []