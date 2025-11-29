from Pedido.models import Bodega, Estanteria, HistorialMovimiento, Item, Producto

def crear_bodega(data: dict) -> Bodega:
    bodega = Bodega.objects.create(**data)
    return bodega

def get_bodegas():
    queryset = Bodega.objects.all()
    return (queryset)

def crear_estanteria(data: dict) -> Estanteria:
    estanteria = Estanteria.objects.create(**data)
    return estanteria


def registrar_item(data: dict) -> Item:
    item = Item.objects.create(**data)
    return item


