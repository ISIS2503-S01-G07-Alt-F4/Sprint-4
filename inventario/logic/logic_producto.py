from fastapi import APIRouter, Depends, Request
from database.database import get_db
from models.producto import Producto
from models.item import Item
from logic.logic_audit_producer import enviar_evento_auditoria
from security.auth0 import validate_auth0_token

router = APIRouter(
    prefix="/productos",
    tags=["Producto"],
    dependencies=[Depends(validate_auth0_token)]
)

@router.get("/")
async def listar_productos(db=Depends(get_db)) -> list[Producto]:
    """
    Lista todos los productos en la base de datos, excluyendo los items asociados.
    """
    productos = db.productos.find({})
    resultado = []
    for producto in productos:
        resultado.append(Producto.model_validate(producto))
    return resultado

@router.post("/")
async def crear_producto(producto: Producto, request: Request, db=Depends(get_db)):
    """
    Crea un producto nuevo en la base de datos.
    Se basa en el código de barras para verificar si el producto ya existe.
    Ver el modelo ejemplo abajo
    """
    if db.productos.find_one({"_id": producto.codigo_barras}):
        return {"message": "El producto con este código de barras ya existe", "codigo": "ERROR"}
    
    resultado = db.productos.insert_one(producto.model_dump(by_alias=True))
    
    enviar_evento_auditoria(
        user_id="system",
        action="CREATE",
        description=f"Producto creado: {producto.nombre}",
        entity="PRODUCTO",
        entity_id=str(resultado.inserted_id),
        metadata=producto.model_dump(),
        ip=request.client.host
    )
    
    return {"producto_creado": resultado.acknowledged, "codigo": "EXITO", "id_producto": resultado.inserted_id}

@router.put("/{codigo_barras}")
async def actualizar_producto(codigo_barras: str, producto: Producto, request: Request, db=Depends(get_db)):
    """
    Actualiza un producto identificado por su código de barras.
    """
    resultado = db.productos.update_one({"_id": codigo_barras}, {"$set": producto.model_dump()})
    if resultado.matched_count == 0:
        return {"message": "Producto no encontrado", "codigo": "ERROR"}
    
    enviar_evento_auditoria(
        user_id="system",
        action="UPDATE",
        description=f"Producto actualizado: {producto.nombre}",
        entity="PRODUCTO",
        entity_id=codigo_barras,
        metadata=producto.model_dump(),
        ip=request.client.host
    )
    
    return {"producto_actualizado": resultado.acknowledged, "codigo": "EXITO"}

@router.delete("/{codigo_barras}")
async def eliminar_producto(codigo_barras: str, request: Request, db=Depends(get_db)):
    """
    Elimina un producto identificado por su código de barras.
    """
    resultado = db.productos.delete_one({"_id": codigo_barras})
    if resultado.deleted_count == 0:
        return {"message": "Producto no encontrado", "codigo": "ERROR"}
    
    enviar_evento_auditoria(
        user_id="system",
        action="DELETE",
        description=f"Producto eliminado: {codigo_barras}",
        entity="PRODUCTO",
        entity_id=codigo_barras,
        ip=request.client.host
    )
    
    return {"producto_eliminado": resultado.acknowledged, "codigo": "EXITO"}

@router.get("/{codigo_barras}")
async def obtener_producto(codigo_barras: str, db=Depends(get_db)):
    """
    Obtiene un producto identificado por su código de barras.
    """
    producto = db.productos.find_one({"_id": codigo_barras})
    if not producto:
        return {"message": "Producto no encontrado", "codigo": "ERROR"}
    return producto

