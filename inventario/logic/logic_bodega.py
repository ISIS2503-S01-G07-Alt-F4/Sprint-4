from fastapi import APIRouter, Depends
from database.database import get_db
from models.estanteria import Estanteria
from models.bodega import Bodega

router = APIRouter(
    prefix="/bodegas",
    tags=["Bodega"]
)

@router.post("/")
async def crear_bodega(bodega: Bodega, db=Depends(get_db)):
    resultado = db.bodegas.insert_one(bodega.model_dump())
    return {"bodega_creada": resultado.acknowledged, "codigo": "EXITO"}

@router.get("/")
async def listar_bodegas(db=Depends(get_db)) -> list[Bodega]:
    bodegas = db.bodegas.find()
    return bodegas

@router.get("/{bodega_id}")
async def obtener_bodega(bodega_id: str, db=Depends(get_db)):
    bodega = db.bodegas.find_one({"_id": bodega_id})
    return bodega

@router.delete("/{bodega_id}")
async def eliminar_bodega(bodega_id: str, db=Depends(get_db)):
    resultado = db.bodegas.delete_one({"_id": bodega_id})
    return {"bodega_eliminada": resultado.acknowledged, "codigo": "EXITO"}

@router.put("/{bodega_id}")
async def actualizar_bodega(bodega_id: str, bodega: Bodega, db=Depends(get_db)):
    resultado = db.bodegas.update_one({"_id": bodega_id}, {"$set": bodega.model_dump()})
    return {"bodega_actualizada": resultado.acknowledged, "codigo": "EXITO"}

@router.get("/{bodega_id}/estanterias")
async def listar_estanterias_bodega(bodega_id: str, db=Depends(get_db)):
    bodega = db.bodegas.find_one({"_id": bodega_id})
    if not bodega:
        return {"message": "Bodega no encontrada", "codigo": "ERROR"}
    estanterias = bodega.get("estanterias", [])
    return {"estanterias": estanterias, "codigo": "EXITO"}

@router.post("/{bodega_id}/estanterias")
async def agregar_estanteria_bodega(bodega_id: str, estanteria: Estanteria, db=Depends(get_db)):
    resultado = db.bodegas.update_one(
        {"_id": bodega_id},
        {"$push": {"estanterias": estanteria.model_dump()}}
    )
    return {"estanteria_agregada": resultado.acknowledged, "codigo": "EXITO"}

@router.delete("/{bodega_id}/estanterias/{numero_estanteria}")
async def eliminar_estanteria_bodega(bodega_id: str, numero_estanteria: str, db=Depends(get_db)):
    resultado = db.bodegas.update_one(
        {"_id": bodega_id},
        {"$pull": {"estanterias": {"numero_estanteria": numero_estanteria}}}
    )
    return {"estanteria_eliminada": resultado.acknowledged, "codigo": "EXITO"}