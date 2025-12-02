from typing import Optional
from fastapi import APIRouter, Depends, status, Query
from models.audit_event import AuditEvent, AuditLog, PaginatedAuditLogs
from database.database import get_db, get_next_id
from datetime import datetime

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit-logs"],
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def crear_log_auditoria(audit_event: AuditEvent, db=Depends(get_db)) -> dict:
    """
    Crea un nuevo log de auditoría.
    """
    audit_log_id = get_next_id("audit_log_id")
    audit_log_dict = audit_event.model_dump(by_alias=True)
    
    audit_log_registered_at = datetime.now()
    audit_log_dict["_id"] = audit_log_id
    audit_log_dict["registered_at"] = audit_log_registered_at
    
    res =  db.audit_logs.insert_one(audit_log_dict)
    
    # Actualizar la lista de logs recientes en el servicio auditado
    db.audited_services.update_one(
        {"_id": audit_event.audited_service_id},
        {
            "$push": {"recent_logs": {"$each": [audit_log_dict], "$slice": -10}},
            "$setOnInsert": {"name": audit_event.audited_service_id, "id": audit_event.audited_service_id}
        },
        upsert=True
    )
    
    return {"event created": res.acknowledged, "codigo": "EXITO", "audit_log_id": res.inserted_id}


@router.get("/", status_code=status.HTTP_200_OK)
async def listar_logs_auditoria(
    page: int = Query(1, ge=1), 
    limit: int = Query(10, ge=1, le=100), 
    service_id: Optional[str] = Query(None),
    db=Depends(get_db)
) -> PaginatedAuditLogs:
    """
    Lista todos los logs de auditoría con paginación y filtrado opcional por servicio.
    """
    query = {}
    if service_id:
        query["audited_service_id"] = service_id

    skip = (page - 1) * limit
    total = db.audit_logs.count_documents(query)
    logs = db.audit_logs.find(query).sort("timestamp", -1).skip(skip).limit(limit).to_list(length=limit)
    
    return PaginatedAuditLogs(
        total=total,
        page=page,
        limit=limit,
        data=logs
    )

@router.get("/recent-events", status_code=status.HTTP_200_OK)
async def listar_eventos_recientes(db=Depends(get_db)) -> list[AuditLog]:
    """
    Lista los 10 logs de auditoría más recientes.
    """
    logs =  db.audit_logs.find().sort("timestamp", -1).to_list(length=10)
    return logs