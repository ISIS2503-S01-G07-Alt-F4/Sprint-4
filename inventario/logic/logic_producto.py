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
    """
    Lista todos los productos en la base de datos, excluyendo los items asociados.
    """
    productos = db.productos.find({}, {"atributos": 0})
    return productos

@router.post("/")
async def crear_producto(producto: Producto, db=Depends(get_db)):
    """
    Crea un producto nuevo en la base de datos.
    Se basa en el código de barras para verificar si el producto ya existe.
    Ver el modelo ejemplo abajo
    """
    if db.productos.find_one({"_id": producto.codigo_barras}):
        return {"message": "El producto con este código de barras ya existe", "codigo": "ERROR"}
    
    resultado = db.productos.insert_one(producto.model_dump(by_alias=True))
    return {"producto_creado": resultado.acknowledged, "codigo": "EXITO"}

@router.put("/{codigo_barras}")
async def actualizar_producto(codigo_barras: str, producto: Producto, db=Depends(get_db)):
    """
    Actualiza un producto identificado por su código de barras.
    """
    resultado = db.productos.update_one({"_id": codigo_barras}, {"$set": producto.model_dump()})
    if resultado.matched_count == 0:
        return {"message": "Producto no encontrado", "codigo": "ERROR"}
    return {"producto_actualizado": resultado, "codigo": "EXITO"}

@router.delete("/{codigo_barras}")
async def eliminar_producto(codigo_barras: str, db=Depends(get_db)):
    """
    Elimina un producto identificado por su código de barras.
    """
    resultado = db.productos.delete_one({"_id": codigo_barras})
    return {"producto_eliminado": resultado, "codigo": "EXITO"}

@router.get("/{codigo_barras}")
async def obtener_producto(codigo_barras: str, db=Depends(get_db)):
    """
    Obtiene un producto identificado por su código de barras.
    """
    producto = db.productos.find_one({"_id": codigo_barras})
    return producto

@router.get("/{codigo_barras}/items")
async def obtener_items_producto(codigo_barras: str, db=Depends(get_db)):
    """
    Obtiene todos los items asociados a un producto identificado por su código de barras.
    """
    # Verificar si el producto existe
    producto = db.productos.find_one({"_id": codigo_barras})
    if not producto:
        return {"message": "Producto no encontrado", "codigo": "ERROR"}

    items = db.items.find({"producto_id": codigo_barras})
    items_disponibles = db.itemsDisponibles.find({"producto_id": codigo_barras})
    items = list(items) + list(items_disponibles)
    return {"items": items, "codigo": "EXITO"}

@router.get("/{codigo_barras}/itemsDisponibles")
async def obtener_items_disponibles_producto(codigo_barras: str, db=Depends(get_db)):
    """
    Obtiene todos los items disponibles asociados a un producto identificado por su código de barras.
    """
    # Verificar si el producto existe
    producto = db.productos.find_one({"_id": codigo_barras})
    if not producto:
        return {"message": "Producto no encontrado", "codigo": "ERROR"}

    items_disponibles = db.itemsDisponibles.find({"producto_id": codigo_barras})
    return {"items_disponibles": list(items_disponibles), "codigo": "EXITO"}

@router.get("/{codigo_barras}/items/{item_sku}")
async def obtener_item_de_producto(codigo_barras: str, item_sku: str, db=Depends(get_db)):
    # Verificar si el producto existe
    producto = db.productos.find_one({"codigo_barras": codigo_barras})
    if not producto:
        return {"message": "Producto no encontrado", "codigo": "ERROR"}

    # Buscar el item dentro del producto
    for items in producto.get("items", []):
        if items["sku"] == item_sku:
            item = items
            break
    if not item:
        return {"message": "Item no encontrado en el producto", "codigo": "ERROR"}

    return {"item": item, "codigo": "EXITO"}