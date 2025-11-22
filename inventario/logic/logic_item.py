from fastapi import APIRouter, Depends, HTTPException, status
from database.database import get_db
from models.item import Item
from typing import Dict, Any
router = APIRouter(
    prefix="/items",
    tags=["Item"]
)

@router.get("/{item_sku}", status_code=status.HTTP_200_OK)
async def obtener_item(item_sku: str, db=Depends(get_db)) -> Item:
    """
    Obtiene un item identificado por su SKU.
    """
    item = db.itemsDisponibles.find_one({"_id": item_sku})
    if not item:
        item = db.items.find_one({"_id": item_sku})
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item no encontrado")
    return Item.model_validate(item)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def crear_item(item: Item, db=Depends(get_db)) -> Dict[str, Any]:
    """
    Crea un item nuevo en la base de datos.
    Ver el modelo ejemplo abajo
    """
    # Validar que el SKU no existe
    if db.items.find_one({"_id": item.sku}) or db.itemsDisponibles.find_one({"_id": item.sku}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El item con este SKU ya existe")
    
    # Validar que el producto existe
    if db.productos.find_one({"_id": item.producto_id}) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El producto asociado no existe")
    
    # Validar que la bodega existe
    bodega = db.bodegas.find_one({"_id": item.bodega_id})
    if bodega is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La bodega asociada no existe")
    
    # Validar que la estantería existe dentro de la bodega
    estanteria_existe = False
    for estanteria in bodega.get("estanterias", []):
        if estanteria["_id"] == item.estanteria_id:
            estanteria_existe = True
            break
    
    if not estanteria_existe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La estantería asociada no existe")
    
    # Crear el item
    if item.estado == "disponible":
        resultado = db.itemsDisponibles.insert_one(item.model_dump(by_alias=True))
        # Incrementar el contador de items disponibles en el producto
        db.productos.update_one({"_id": item.producto_id}, {"$inc": {"cantidad_items_disponibles": 1}})
    else:
        resultado = db.items.insert_one(item.model_dump(by_alias=True))
    
    return {"item_creado": resultado.acknowledged, "codigo": "EXITO", "id_item": str(resultado.inserted_id)}

@router.put("/{item_sku}", status_code=status.HTTP_200_OK)
async def actualizar_item(item_sku: str, item: Item, db=Depends(get_db)) -> Dict[str, Any]:
    """
    Actualiza un item identificado por su SKU.
    """
    resultado = db.items.update_one({"_id": item_sku}, {"$set": item.model_dump(by_alias=True)})
    if resultado.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item no encontrado")
    return {"item_actualizado": resultado.acknowledged, "codigo": "EXITO"}
@router.delete("/{item_sku}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_item(item_sku: str, db=Depends(get_db)):
    # Obtener el item antes de eliminarlo
    item = db.items.find_one({"_id": item_sku})
    
    # Si no está en items, buscar en itemsDisponibles
    if not item:
        item = db.itemsDisponibles.find_one({"_id": item_sku})
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item no encontrado")
        # Eliminar de itemsDisponibles
        db.itemsDisponibles.delete_one({"_id": item_sku})
        # Decrementar el contador de items disponibles
        db.productos.update_one({"_id": item["producto_id"]}, {"$inc": {"cantidad_items_disponibles": -1}})
    else:
        # Eliminar de items
        db.items.delete_one({"_id": item_sku})

@router.get("/", status_code=status.HTTP_200_OK)
async def listar_items(db=Depends(get_db)) -> list[Item]:
    items = db.items.find()
    return [Item.model_validate(item) for item in items]

@router.get("/productoBodega", status_code=status.HTTP_200_OK)
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

@router.get("/estanteria/disponibles", status_code=status.HTTP_200_OK)
async def obtener_items_estanteria_disponibles(bodega_id: str, numero_estanteria: str, db=Depends(get_db)) -> Dict[str, Any]:
    """
    Obtiene todos los items disponibles en una estantería específica dentro de una bodega.
    """
    # Verificar si la bodega existe
    bodega = db.bodegas.find_one({"_id": bodega_id})
    if not bodega:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bodega no encontrada")
    
    # Verificar si la estantería existe dentro de la bodega
    estanteria_existe = False
    for estanteria in bodega.get("estanterias", []):
        if estanteria["numero_estanteria"] == numero_estanteria:
            estanteria_existe = True
            break
    
    if not estanteria_existe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estantería no encontrada")
    
    # Obtener los items disponibles en la estantería
    items_disponibles = db.itemsDisponibles.find({"bodega_id": bodega_id, "estanteria_id": numero_estanteria})
    return {"items_disponibles": list(items_disponibles), "codigo": "EXITO"}

@router.get("/estanteria/todos", status_code=status.HTTP_200_OK)
async def obtener_items_estanteria_todos(bodega_id: str, numero_estanteria: str, db=Depends(get_db)) -> Dict[str, Any]:
    """
    Obtiene todos los items (disponibles y no disponibles) en una estantería específica dentro de una bodega.
    """
    # Verificar si la bodega existe
    bodega = db.bodegas.find_one({"_id": bodega_id})
    if not bodega:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bodega no encontrada")
    
    # Verificar si la estantería existe dentro de la bodega
    estanteria_existe = False
    for estanteria in bodega.get("estanterias", []):
        if estanteria["numero_estanteria"] == numero_estanteria:
            estanteria_existe = True
            break
    
    if not estanteria_existe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estantería no encontrada")
    
    # Obtener todos los items en la estantería
    items = db.items.find({"bodega_id": bodega_id, "estanteria_id": numero_estanteria})
    items_disponibles = db.itemsDisponibles.find({"bodega_id": bodega_id, "estanteria_id": numero_estanteria})
    items = list(items) + list(items_disponibles)
    return {"items": items, "codigo": "EXITO"}