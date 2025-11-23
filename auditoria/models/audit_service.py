from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated, List
from models.audit_event import AuditEvent, SimpleAuditEvent

class AuditService(BaseModel):
    name: Annotated[str, StringConstraints(min_length=2, max_length=100)]
    recent_events: List[AuditEvent] = []