from fastapi import APIRouter, Depends
from database.database import get_db
from models.producto import Producto
from models.item import Item    
router = APIRouter(
    prefix="/productos",
    tags=["Producto"]
)

@router.get("/")
async def listar_productos(db=Depends(get_db)) -> list[Producto]:
    productos = db.productos.find({}, {"items": 0})
    return productos

@router.post("/")
async def crear_producto(producto: Producto, db=Depends(get_db)):
    if db.productos.find_one({"codigo_barras": producto.codigo_barras}):
        return {"message": "El producto con este código de barras ya existe", "codigo": "ERROR"}
    
    resultado = db.productos.insert_one(producto.model_dump())
    return {"producto_creado": resultado.acknowledged, "codigo": "EXITO"}

@router.put("/{codigo_barras}")
async def actualizar_producto(codigo_barras: str, producto: Producto, db=Depends(get_db)):
    resultado = db.productos.update_one({"codigo_barras": codigo_barras}, {"$set": producto.model_dump()})
    return {"producto_actualizado": resultado, "codigo": "EXITO"}

@router.delete("/{codigo_barras}")
async def eliminar_producto(codigo_barras: str, db=Depends(get_db)):
    resultado = db.productos.delete_one({"codigo_barras": codigo_barras})
    return {"producto_eliminado": resultado, "codigo": "EXITO"}

@router.get("/{codigo_barras}")
async def obtener_producto(codigo_barras: str, db=Depends(get_db)):
    producto = db.productos.find_one({"codigo_barras": codigo_barras})
    return producto

@router.get("/{codigo_barras}/items")
async def obtener_items_producto(codigo_barras: str, db=Depends(get_db)):
    # Verificar si el producto existe
    producto = db.productos.find_one({"codigo_barras": codigo_barras})
    if not producto:
        return {"message": "Producto no encontrado", "codigo": "ERROR"}

    items = producto.get("items", [])
    return {"items": items, "codigo": "EXITO"}

@router.post("/{codigo_barras}/items")
async def agregar_item_a_producto(codigo_barras: str, item: Item, db=Depends(get_db)):
    # Verificar si el producto existe
    producto = db.productos.find_one({"codigo_barras": codigo_barras})
    if not producto:
        return {"message": "Producto no encontrado", "codigo": "ERROR"}
    # Si el item no existe, se crea
    item = db.items.find_one({"sku": item.sku})
    if not item:
        item = db.items.insert_one(item.model_dump())

    # Agregar el item al producto
    db.productos.update_one(
        {"codigo_barras": codigo_barras},
        {"$push": {"items": item}}
    )
    return {"message": "Item agregado al producto", "codigo": "EXITO"}

@router.get("/{codigo_barras}/items/{item_sku}")
async def obtener_item_de_producto(codigo_barras: str, item_sku: str, db=Depends(get_db)):
    # Verificar si el producto existe
    producto = db.productos.find_one({"codigo_barras": codigo_barras})
    if not producto:
        return {"message": "Producto no encontrado", "codigo": "ERROR"}

    # Buscar el item dentro del producto
    item = next((itm for itm in producto.get("items", []) if itm["sku"] == item_sku), None)
    if not item:
        return {"message": "Item no encontrado en el producto", "codigo": "ERROR"}

    return {"item": item, "codigo": "EXITO"}

@router.put("/{codigo_barras}/items/{item_sku}")
async def actualizar_item_de_producto(codigo_barras: str, item: Item, db=Depends(get_db)):
    # Verificar si el producto existe
    producto = db.productos.find_one({"codigo_barras": codigo_barras})
    if not producto:
        return {"message": "Producto no encontrado", "codigo": "ERROR"}

    # Actualizar el item dentro del producto
    resultado = db.productos.update_one(
        {"codigo_barras": codigo_barras, "items.sku": item.sku},
        {"$set": {f"items.$.{k}": v for k, v in item.model_dump().items()}}
    )
    return {"item_actualizado_en_producto": resultado, "codigo": "EXITO"}

@router.delete("/{codigo_barras}/items/{item_sku}")
async def eliminar_item_de_producto(codigo_barras: str, item_sku: str, db=Depends(get_db)):
    # Verificar si el producto existe
    producto = db.productos.find_one({"codigo_barras": codigo_barras})
    if not producto:
        return {"message": "Producto no encontrado", "codigo": "ERROR"}

    # Eliminar el item del producto
    resultado = db.productos.update_one(
        {"codigo_barras": codigo_barras},
        {"$pull": {"items": {"sku": item_sku}}}
    )
    return {"item_eliminado_del_producto": resultado, "codigo": "EXITO"}