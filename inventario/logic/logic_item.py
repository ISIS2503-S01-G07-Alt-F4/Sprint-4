from fastapi import APIRouter, Depends
from database.database import get_db
from models.item import Item
router = APIRouter(
    prefix="/items",
    tags=["Item"]
)

@router.get("/{item_sku}")
async def obtener_item(item_sku: str, db=Depends(get_db)):
    """
    Obtiene un item identificado por su SKU.
    """
    item = db.itemsDisponibles.find_one({"_id": item_sku})
    if not item:
        item = db.items.find_one({"_id": item_sku})
        if not item:
            return {"message": "Item no encontrado", "codigo": "ERROR"}
    return {"item": item, "codigo": "EXITO"}

@router.post("/")
async def crear_item(item: Item, db=Depends(get_db)):
    """
    Crea un item nuevo en la base de datos.
    Ver el modelo ejemplo abajo
    """
    if db.items.find_one({"_id": item.sku}) or db.itemsDisponibles.find_one({"_id": item.sku}):
        return {"message": "El item con este SKU ya existe", "codigo": "ERROR"}
    if db.productos.find_one({"_id": item.producto_id}) is None:
        return {"message": "El producto asociado no existe", "codigo": "ERROR"}
    bodega = db.bodegas.find_one({"_id": item.bodega_id})
    if bodega is None:
        return {"message": "La bodega asociada no existe", "codigo": "ERROR"}
    
    for estanteria in bodega.get("estanterias", []):
        if estanteria["numero_estanteria"] == item.numero_estanteria:
            break
    if item.estado == "disponible":
        resultado = db.itemsDisponibles.insert_one(item.model_dump())
        db.productos.update_one({"_id": item.producto_id}, {"$inc": {"cantidad_items_disponibles": 1}})  # Incrementar el contador de items disponibles en el producto
    else:
        resultado = db.items.insert_one(item.model_dump())
    

    return {"item_creado": resultado.acknowledged, "codigo": "EXITO"}

@router.put("/{item_sku}")
async def actualizar_item(item_sku: str, item: Item, db=Depends(get_db)):
    """
    Actualiza un item identificado por su SKU.
    """
    resultado = db.items.update_one({"_id": item_sku}, {"$set": item.model_dump()})
    if resultado.matched_count == 0:
        return {"message": "Item no encontrado", "codigo": "ERROR"}
    return {"item_actualizado": resultado.acknowledged, "codigo": "EXITO"}
@router.delete("/{item_sku}")
async def eliminar_item(item_sku: str, db=Depends(get_db)):

    item = db.items.find_one({"sku": item_sku})
    resultado = db.items.delete_one({"sku": item_sku})
    db.productos.update_one({"_id": item["producto_id"]}, {"$pull": {"items": {"sku": item_sku}}}) # Eliminar la referencia del item en el producto
    return {"item_eliminado": resultado}