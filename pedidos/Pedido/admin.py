from django.contrib import admin
from .models import Bodega, Cliente, Estanteria, Factura, Pedido, Producto, Item, HistorialMovimiento, ProductoSolicitado
# Register your models here.
admin.site.register(Bodega)
admin.site.register(Estanteria)
admin.site.register(Producto)
admin.site.register(Item)
admin.site.register(HistorialMovimiento)
admin.site.register(Pedido)
admin.site.register(Cliente)
admin.site.register(ProductoSolicitado)
admin.site.register(Factura)