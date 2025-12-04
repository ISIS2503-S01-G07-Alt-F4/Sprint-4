import hashlib
import hmac
import json
import os
from django.db import models

from Provesi.middleware.current_request import get_current_request


class Cliente(models.Model):
    id = models.AutoField(primary_key=True)  
    nombre = models.CharField(max_length=100)
    numero_telefono = models.CharField(max_length=15)

class Factura(models.Model):
    #id = models.CharField(max_length=50, primary_key=True) No tiene ninguna utilidad real que el id no sea autogenerado sino que sea artificial, nos complicamos más
    id= models.AutoField(primary_key=True) 
    costo_total = models.FloatField()
    metodo_pago = models.CharField(max_length=50)
    num_cuenta = models.CharField(max_length=50)
    comprobante = models.CharField(max_length=100)

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="facturas")

class Pedido(models.Model):
    class Estado(models.TextChoices):
        TRANSITO = "Transito", "Transito"
        ALISTAMIENTO = "Alistamiento", "Alistamiento"
        POR_VERIFICAR = "Por verificar", "Por verificar"
        RECHAZADOXVERIFICAR = "Rechazado x verificar", "Rechazado x verificar"
        VERIFICADO = "Verificado","Verificado"
        EMPACADOXDESPACHAR = "Empacado x despachar", "Empacado x despachar"
        DESPACHADO = "Despachado", "Despachado"
        DESPACHADOXFACTURAR = "Despachado x facturar", "Despachado x facturar"
        ENTREGADO = "Entregado", "Entregado"
        DEVUELTO  = "Devuelto","Devuelto"
        PRODUCCION = "Produccion", "Produccion"
        BORDADO = "Bordado", "Bordado"
        DROPSHIPPING = "Dropshipping", "Dropshipping"
        COMPRA = "Compra", "Compra"
        ANULADO = "Anulado", "Anulado"
        

    estado = models.CharField(
        max_length=30,
        choices=Estado.choices,
        default=Estado.ALISTAMIENTO
    )
    id = models.AutoField(primary_key=True)
    items = models.JSONField(default=list, blank=True)
    factura = models.OneToOneField(Factura,on_delete=models.CASCADE,related_name="pedido",null=True,blank=True)
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE, related_name='pedidos', null=True, blank=True)
    operario = models.CharField(max_length=100, blank=True)
    bodega_id = models.CharField(max_length=100, blank=True)
    hash_de_integridad = models.CharField(max_length=64, editable=False, blank=True)

    def _datos_para_hash(self):
        datos_factura = None
        if self.factura:
            datos_factura = {
                "id": self.factura.id,
                "costo_total": self.factura.costo_total,
                "metodo_pago": self.factura.metodo_pago,
                "num_cuenta": self.factura.num_cuenta,
                "comprobante": self.factura.comprobante,
                "cliente_id": self.factura.cliente_id,
            }
        productos = list(
            self.productos_solicitados.all().values('producto', 'cantidad')
        ) if hasattr(self, 'productos_solicitados') else []

        datos = {
            "id": self.id,
            "estado": self.estado,
            "cliente": self.cliente_id,
            "factura": datos_factura,
            "items": list(self.items or []),
            "bodega_id": self.bodega_id,
            "productos_solicitados": productos,
        }
        return json.dumps(datos, sort_keys=True).encode()

    def generar_hash(self):
        INTEGRITY_KEY = os.getenv("INTEGRITY_KEY")
        if not INTEGRITY_KEY:
            raise RuntimeError("Falta INTEGRITY_KEY en las variables de entorno")
        return hmac.new(INTEGRITY_KEY.encode(), self._datos_para_hash(), hashlib.sha256).hexdigest()

    
    # Siempre recalcula hash salvo en admin
    def save(self, *args, **kwargs):
        
        super().save(*args, **kwargs)
        request = get_current_request()
        if request is None:
            return
        if request.path.startswith("/admin/"):
            return
        
        self.hash_de_integridad = self.generar_hash()
        super().save(update_fields=["hash_de_integridad"])

    def verificar_integridad(self):
        print("codigo 1 "+self.hash_de_integridad)
        print("codigo 2 "+self.generar_hash())
        return hmac.compare_digest(self.hash_de_integridad, self.generar_hash())



class ProductoSolicitado(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='productos_solicitados')
    producto = models.CharField(max_length=100)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"Pedido {self.pedido_id}: {self.cantidad} x {self.producto}"