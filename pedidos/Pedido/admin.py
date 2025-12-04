from django.contrib import admin
from .models import Cliente, Factura, Pedido, ProductoSolicitado


admin.site.register(Pedido)
admin.site.register(Cliente)
admin.site.register(ProductoSolicitado)
admin.site.register(Factura)