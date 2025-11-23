from fastapi import APIRouter, Depends, HTTPException, status
from models.audit_event import AuditEvent, AuditLog
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
    
    #Verificar que el servicio auditado existe
    audited_service =  db.audited_services.find_one({"_id": audit_event.audited_service_id})
    if not audited_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audited service not found")
    
    audit_log_registered_at = datetime.now()
    audit_log_dict["_id"] = audit_log_id
    audit_log_dict["registered_at"] = audit_log_registered_at
    
    res =  db.audit_logs.insert_one(audit_log_dict)
    
    # Actualizar la lista de logs recientes en el servicio auditado
    db.audited_services.update_one(
        {"_id": audit_event.audited_service_id},
        {"$push": {"recent_logs": {"$each": [audit_log_dict], "$slice": -10}}}
    )
    
    return {"event created": res.acknowledged, "codigo": "EXITO", "audit_log_id": res.inserted_id}


@router.get("/", status_code=status.HTTP_200_OK)
async def listar_logs_auditoria(db=Depends(get_db)) -> list[AuditLog]:
    """
    Lista todos los logs de auditoría de los más recientes a los más antiguos.
    """
    logs =  db.audit_logs.find().sort("timestamp", -1).to_list(length=100)
    return logs

@router.get("/recent-events", status_code=status.HTTP_200_OK)
async def listar_eventos_recientes(db=Depends(get_db)) -> list[AuditLog]:
    """
    Lista los 10 logs de auditoría más recientes.
    """
    logs =  db.audit_logs.find().sort("timestamp", -1).to_list(length=10)
    return logs