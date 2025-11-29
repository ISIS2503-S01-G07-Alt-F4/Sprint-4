


from Pedido.models import Factura
from django.db import transaction

def crear_factura_para_pedido(pedido, datos_factura):
    """
    Crea una factura para un pedido y calcula el costo total automáticamente
    """
    try:
        with transaction.atomic():
            # Calcular costo total sumando los precios de todos los items
            costo_total = 0
            for item in pedido.items.all():
                costo_total += float(item.producto.precio)
            
            # Crear la factura
            factura = Factura.objects.create(
                costo_total=costo_total,  
                metodo_pago=datos_factura['metodo_pago'],
                num_cuenta=datos_factura['num_cuenta'],
                comprobante=datos_factura['comprobante'],
                cliente=pedido.cliente
            )
            
            
            
            return factura, None
            
    except Exception as e:
        return None, f"Error creando factura: {str(e)}"