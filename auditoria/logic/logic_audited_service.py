from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from models.audited_service import AuditedService, Service
from database.database import get_db, get_next_id

router = APIRouter(
    prefix="/audited-services",
    tags=["Audited-services"],
)
db = get_db()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def crear_servicio_auditado(service: Service, db=db) -> Dict[str, Any]:
    """
    Crea un nuevo servicio auditado.
    """
    audited_service_id = get_next_id("audited_service_id")
    audited_service_dict = {
        "_id": audited_service_id,
        "id": audited_service_id,
        "name": service.name,
        "recent_logs": []
    }
    res =  db.audited_services.insert_one(audited_service_dict)
    return {"log created": res.acknowledged, "codigo": "EXITO", "audited_service_id": res.inserted_id}

@router.get("/", status_code=status.HTTP_200_OK)
async def listar_servicios_auditados(db=Depends(get_db)) -> list[AuditedService]:
    """
    Lista todos los servicios auditados.
    """
    servicios = db.audited_services.find({}, {"recent_logs": 0}).to_list()
    return servicios

@router.get("/{audited_service_id}", status_code=status.HTTP_200_OK) 
async def get_servicio_auditado(audited_service_id: str, db=Depends(get_db)) -> AuditedService:
    """
    Obtiene un servicio auditado por su ID.
    """
    audited_service =  db.audited_services.find_one({"_id": audited_service_id})
    if not audited_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audited service not found")
    return audited_service

@router.delete("/{audited_service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_servicio_auditado(audited_service_id: str, db=Depends(get_db)) -> None:
    """
    Elimina un servicio auditado por su ID.
    """
    resultado =  db.audited_services.delete_one({"_id": audited_service_id})
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audited service not found")
    
    #Eliminar logs de auditoría asociados
    db.audit_events.delete_many({"audited_service_id": audited_service_id})
    return None

@router.put("/{audited_service_id}", status_code=status.HTTP_200_OK)
async def actualizar_servicio_auditado(audited_service_id: str, audited_service: AuditedService, db=Depends(get_db)) -> Dict[str, Any]:
    """
    Actualiza un servicio auditado por su ID.
    """
    resultado =  db.audited_services.update_one(
        {"_id": audited_service_id},
        {"$set": audited_service.model_dump(exclude={"recent_logs"})}
    )
    if resultado.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audited service not found")
    
    return {"Audited service updated": resultado.acknowledged, "codigo": "EXITO"}

@router.get("/{audited_service_id}/recent-events", status_code=status.HTTP_200_OK)
async def obtener_logs_recientes_servicio(audited_service_id: str, db=Depends(get_db)) -> list[Dict[str, Any]]:
    """
    Obtiene los logs recientes de un servicio auditado.
    """
    audited_service =  db.audited_services.find_one({"_id": audited_service_id})
    if not audited_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audited service not found")
    
    logs = audited_service.get("recent_logs", [])
    return logs

@router.get("/{audited_service_id}/all-events", status_code=status.HTTP_200_OK)
async def obtener_todos_logs_servicio(audited_service_id: str, db=Depends(get_db)) -> list[Dict[str, Any]]:
    """
    Obtiene todos los logs de un servicio auditado.
    """
    audited_service =  db.audited_services.find_one({"_id": audited_service_id})
    if not audited_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audited service not found")
    
    logs =  db.audit_logs.find({"audited_service_id": audited_service_id}).sort("timestamp", -1).to_list()
    return logs