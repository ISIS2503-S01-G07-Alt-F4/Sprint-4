from fastapi import APIRouter, Depends, HTTPException, status
from models.audit_event import AuditEvent
from database.database import get_db, get_next_id

router = APIRouter(
    prefix="/audit-events",
    tags=["Audit-events"],
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def crear_evento_auditoria(audit_event: AuditEvent, db=Depends(get_db)) -> dict:
    """
    Crea un nuevo evento de auditoría.
    """
    audit_event_id = get_next_id("audit_event_id")
    audit_event_dict = audit_event.model_dump(by_alias=True)
    
    #Verificar que el servicio auditado existe
    audited_service =  db.audited_services.find_one({"_id": audit_event.audited_service_id})
    if not audited_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audited service not found")
    
    audit_event_dict["_id"] = audit_event_id
    
    res =  db.audit_events.insert_one(audit_event_dict)
    
    # Actualizar la lista de eventos recientes en el servicio auditado
    db.audited_services.update_one(
        {"_id": audit_event.audited_service_id},
        {"$push": {"recent_events": {"$each": [audit_event_dict], "$slice": -10}}}
    )
    
    return {"event created": res.acknowledged, "codigo": "EXITO", "audit_event_id": res.inserted_id}


@router.get("/", status_code=status.HTTP_200_OK)
async def listar_eventos_auditoria(db=Depends(get_db)) -> list[AuditEvent]:
    """
    Lista todos los eventos de auditoría de los más recientes a los más antiguos.
    """
    eventos =  db.audit_events.find().sort("timestamp", -1).to_list(length=100)
    return eventos