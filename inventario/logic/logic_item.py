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
    item = db.items.find_one({"sku": item_sku})
    return item

@router.delete("/{item_sku}")
async def eliminar_item(item_sku: str, db=Depends(get_db)):
    """
    
    """
    item = db.items.find_one({"sku": item_sku})
    resultado = db.items.delete_one({"sku": item_sku})
    db.productos.update_one({"_id": item["producto_id"]}, {"$pull": {"items": {"sku": item_sku}}}) # Eliminar la referencia del item en el producto
    return {"item_eliminado": resultado}