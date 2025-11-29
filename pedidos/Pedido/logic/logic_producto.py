
from Pedido.models import Producto

def obtener_producto(codigo_barras: str):
    try:
        producto = Producto.objects.get(codigo_barras=codigo_barras)
        return producto
    except Producto.DoesNotExist:
        return None
    
def registrar_producto(data: dict) -> Producto:
    if obtener_producto(data['codigo_barras']) is not None:
        raise ValueError("El producto con este código de barras ya existe.")
    producto = Producto.objects.create(**data)
    return producto

def obtener_productos():
    queryset = Producto.objects.all()
    return (queryset)