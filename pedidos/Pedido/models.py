import hashlib
import hmac
import json
import os
import sys
from django.db import models

from Provesi import settings
from Provesi.middleware.current_request import get_current_request
# Create your models here.


class Bodega(models.Model):
    ciudad = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    
    def __str__(self):
        return f"{self.ciudad} - {self.direccion}"
    
class Estanteria(models.Model):
    area_bodega = models.CharField(max_length=100)
    numero_estanteria = models.CharField(max_length=50)
    bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE, related_name="estanterias")  
    
    def __str__(self):
        return f"#{self.numero_estanteria} - Área {self.area_bodega}"
    
class Producto(models.Model):
    codigo_barras = models.CharField(max_length=100, unique=True)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    especificaciones = models.TextField()
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    estanteria = models.ForeignKey(Estanteria, on_delete=models.DO_NOTHING, related_name="productos")  # No on_delete porque es agregación
    
    def __str__(self):
        return f"{self.nombre} ({self.codigo_barras})"
 
class HistorialMovimiento(models.Model):
    operario_responsable = models.ForeignKey('Users.Operario', on_delete=models.DO_NOTHING)
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    tipo_movimiento = models.CharField(max_length=50, choices=[('Ingreso', 'Ingreso'), ('Retiro', 'Retiro')])
       
class Item(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="items")  
    sku = models.CharField(max_length=100, unique=True) # identificador único
    ingreso = models.ForeignKey(HistorialMovimiento, on_delete=models.CASCADE, related_name='ingresos')
    retiro = models.ForeignKey(HistorialMovimiento, on_delete=models.SET_NULL, null=True, blank=True)
    



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
    items = models.ManyToManyField('Item', related_name='pedidos')  
    factura = models.OneToOneField(Factura,on_delete=models.CASCADE,related_name="pedido",null=True,blank=True)
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE, related_name='pedidos', null=True, blank=True)
    operario = models.ForeignKey('Users.Operario', on_delete=models.DO_NOTHING, null=True, blank=True)
    hash_de_integridad = models.CharField(max_length=64, editable=False, null=True, blank=True)

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
        datos = {
            "id": self.id,
            "estado": self.estado,
            "cliente": self.cliente_id,
            "factura": datos_factura,
            "items": list(self.items.values_list('sku', flat=True)),
        }
        return json.dumps(datos, sort_keys=True).encode()

    def generar_hash(self):
        INTEGRITY_KEY = os.getenv("INTEGRITY_KEY")
        if not INTEGRITY_KEY:
            raise Exception("Falta INTEGRITY_KEY en las variables de entorno")
        print("___datos___")
        print(self._datos_para_hash())
        print("___________")
        return hmac.new(INTEGRITY_KEY.encode(), self._datos_para_hash(), hashlib.sha256).hexdigest()

    
    # super().save(*args, **kwargs)
    # if 'manage.py' in sys.argv:
    #     return
    # recalcular_hash = os.getenv("RECALCULAR_HASH")

    # if recalcular_hash!=None:
    #     print("recalculo")
    #     print(recalcular_hash)
    #     self.hash_de_integridad = self.generar_hash()
    #     super().save(update_fields=['hash_de_integridad'])
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
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="productos_solicitados")
    cantidad = models.PositiveIntegerField()
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"





    

# class Envio(models.Model):
#     id_envio = models.AutoField(primary_key=True)  
#     direccion = models.CharField(max_length=200)
#     ciudad = models.CharField(max_length=100)
#     #imagen = models.ImageField(upload_to="envios/", null=True, blank=True) Esto de momento lo comentamos porque no sabemos como funciona
#     fecha_envio = models.DateField()

