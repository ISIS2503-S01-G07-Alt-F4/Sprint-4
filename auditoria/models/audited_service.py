from pydantic import BaseModel, StringConstraints
from typing import Annotated, List, Optional
from models.audit_event import AuditEvent

class AuditedService(BaseModel):
    id : Optional[str] = None
    name: Annotated[str, StringConstraints(min_length=2, max_length=100)]
    recent_events: List[AuditEvent] = []
    
    def __str__(self) -> str:
        return f"{self.name}"