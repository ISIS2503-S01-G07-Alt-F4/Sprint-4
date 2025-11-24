from fastapi import APIRouter, Depends, HTTPException, status
from database.database import get_db
from models.estanteria import Estanteria
from typing import Dict, Any

router = APIRouter(
    prefix="/estanterias",
    tags=["Estanteria"]
)

@router.get("/", status_code=status.HTTP_200_OK)
async def listar_estanterias(db=Depends(get_db)) -> list[Estanteria]:
    """
    Lista todas las estanterías en la base de datos.
    """
    estanterias = db.bodegas.find({}, {"estanterias": 1})
    resultado = []
    for bodega in estanterias:
        for estanteria in bodega.get("estanterias", []):
            resultado.append(Estanteria.model_validate(estanteria))
    return resultado

@router.get("/{bodega_id}", status_code=status.HTTP_200_OK)
async def obtener_estanterias_bodega(bodega_id: str, db=Depends(get_db)) -> list[Estanteria]:
    """
    Obtiene las estanterías de una bodega específica.
    """
    bodega = db.bodegas.find_one({"_id": bodega_id})
    if not bodega:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bodega no encontrada")
    estanterias = bodega.get("estanterias", [])
    return [Estanteria.model_validate(est) for est in estanterias]

@router.post("/{bodega_id}", status_code=status.HTTP_201_CREATED)
async def agregar_estanteria_bodega(bodega_id: str, estanteria: Estanteria, db=Depends(get_db)) -> Dict[str, Any]:
    """
    Agrega una estantería a una bodega específica.
    """
    resultado = db.bodegas.update_one(
        {"_id": bodega_id},
        {"$push": {"estanterias": estanteria.model_dump(by_alias=True)}}
    )
    if resultado.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bodega no encontrada")
    return {"estanteria_agregada": resultado.acknowledged, "codigo": "EXITO"} 

@router.get("/{bodega_id}/{numero_estanteria}", status_code=status.HTTP_200_OK)
async def obtener_estanteria_bodega(bodega_id: str, numero_estanteria: str, db=Depends(get_db)) -> Estanteria:
    bodega = db.bodegas.find_one({"_id": bodega_id})
    if not bodega:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bodega no encontrada")
    estanterias = bodega.get("estanterias", [])
    for estanteria in estanterias:
        if estanteria["numero_estanteria"] == numero_estanteria:
            return Estanteria.model_validate(estanteria)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estantería no encontrada")

@router.put("/{bodega_id}/{numero_estanteria}", status_code=status.HTTP_200_OK)
async def actualizar_estanteria_bodega(bodega_id: str, numero_estanteria: str, estanteria: Estanteria, db=Depends(get_db)) -> Dict[str, Any]:
    if estanteria.numero_estanteria != numero_estanteria:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No es posible cambiar el número de estantería")
    
    resultado = db.bodegas.update_one(
        {"_id": bodega_id, "estanterias._id": numero_estanteria},
        {"$set": {"estanterias.$": estanteria.model_dump(by_alias=True)}}
    )
    if resultado.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bodega o estantería no encontrada")
    return {"estanteria_actualizada": resultado.acknowledged, "codigo": "EXITO"}

@router.delete("/{bodega_id}/{numero_estanteria}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_estanteria_bodega(bodega_id: str, numero_estanteria: str, db=Depends(get_db)):
    resultado = db.bodegas.update_one(
        {"_id": bodega_id},
        {"$pull": {"estanterias": {"_id": numero_estanteria}}}
    )
    # Eliminar items asociados a la estantería para mantener consistencia
    db.itemsDisponibles.delete_many({"bodega_id": bodega_id, "estanteria_id": numero_estanteria})
    db.items.delete_many({"bodega_id": bodega_id, "estanteria_id": numero_estanteria})
    
    if resultado.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bodega no encontrada")
    if resultado.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estantería no encontrada")
    return {"estanteria_eliminada": resultado.acknowledged, "codigo": "EXITO"}