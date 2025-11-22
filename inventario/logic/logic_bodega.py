from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from database.database import get_db, get_next_id
from models.item import Item
from models.estanteria import Estanteria
from models.bodega import Bodega

router = APIRouter(
    prefix="/bodegas",
    tags=["Bodega"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def crear_bodega(bodega: Bodega, db=Depends(get_db)) -> Dict[str, Any]:
    bodega_dict = bodega.model_dump(by_alias=True)
    bodega_dict["_id"] = get_next_id("bodegas")
    resultado = db.bodegas.insert_one(bodega_dict)
    return {"bodega_creada": resultado.acknowledged, "codigo": "EXITO", "id_bodega": resultado.inserted_id}

@router.get("/", status_code=status.HTTP_200_OK)
async def listar_bodegas(db=Depends(get_db)) -> list[Bodega]:
    bodegas = db.bodegas.find({}, {"estanterias": 0}).to_list()
    return [Bodega.model_validate(bodega) for bodega in bodegas]

@router.get("/{bodega_id}", status_code=status.HTTP_200_OK)
async def obtener_bodega(bodega_id: str, db=Depends(get_db)) -> Bodega:
    bodega = db.bodegas.find_one({"_id": bodega_id})
    if not bodega:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bodega no encontrada")
    return Bodega.model_validate(bodega)

@router.delete("/{bodega_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_bodega(bodega_id: str, db=Depends(get_db)):
    resultado = db.bodegas.delete_one({"_id": bodega_id})
    
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bodega no encontrada")
    
    # Eliminar items asociados a la bodega para mantener consistencia
    db.items.delete_many({"bodega_id": bodega_id})
    db.itemsDisponibles.delete_many({"bodega_id": bodega_id})

@router.put("/{bodega_id}", status_code=status.HTTP_200_OK)
async def actualizar_bodega(bodega_id: str, bodega: Bodega, db=Depends(get_db)) -> Dict[str, Any]:
    resultado = db.bodegas.update_one({"_id": bodega_id}, {"$set": bodega.model_dump(by_alias=True)})
    if resultado.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bodega no encontrada")
    return {"bodega_actualizada": resultado.acknowledged, "codigo": "EXITO"}

@router.get("/items", status_code=status.HTTP_200_OK)
async def obtener_items_producto_bodega(codigo_barras: str, bodega_id: str, db=Depends(get_db)) -> Dict[str, Any]:
    """
    Obtiene todos los items asociados a un producto identificado por su código de barras y a una bodega.
    """
    # Verificar si el producto existe
    producto = db.productos.find_one({"_id": codigo_barras})
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    items = db.items.find({"producto_id": codigo_barras, "bodega_id": bodega_id})
    items_disponibles = db.itemsDisponibles.find({"producto_id": codigo_barras, "bodega_id": bodega_id})
    items = list(items) + list(items_disponibles)
    return {"items": items, "codigo": "EXITO"}

@router.get("/itemsDisponibles", status_code=status.HTTP_200_OK)
async def obtener_items_disponibles_producto_bodega(codigo_barras: str, bodega_id: str, db=Depends(get_db)) -> Dict[str, Any]:
    """
    Obtiene todos los items disponibles para un pedido que están
    asociados a un producto identificado por su código de barras.
    """
    # Verificar si el producto existe
    producto = db.productos.find_one({"_id": codigo_barras})
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    items_disponibles = db.itemsDisponibles.find({"producto_id": codigo_barras, "bodega_id": bodega_id})
    return {"items_disponibles": list(items_disponibles), "codigo": "EXITO"}