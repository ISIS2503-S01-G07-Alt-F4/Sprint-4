from rest_framework import serializers
from .models import Cliente, Item, Pedido, Producto, Estanteria, Bodega, ProductoSolicitado
from Pedido.logic.logic_usuario import obtener_operario


class ProductoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Producto
    """
    estanteria_info = serializers.SerializerMethodField(read_only=True)
    bodega_info = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Producto
        fields = [
            'id',
            'codigo_barras', 
            'nombre', 
            'tipo', 
            'especificaciones', 
            'precio', 
            'estanteria',
            'estanteria_info',
            'bodega_info'
        ]

    def get_estanteria_info(self, obj):
        if obj.estanteria:
            return {
                'area_bodega': obj.estanteria.area_bodega,
                'numero_estanteria': obj.estanteria.numero_estanteria,
            }
        return None
    
    def get_bodega_info(self, obj):
        if obj.estanteria and obj.estanteria.bodega:
            bodega = obj.estanteria.bodega
            return {
                'ciudad': bodega.ciudad,
                'direccion': bodega.direccion
            }
        return None
    

class ProductoCreateSerializer(serializers.ModelSerializer):
    """
    Serializer específico para la creación de productos con validaciones adicionales
    """
    class Meta:
        model = Producto
        fields = [
            'codigo_barras', 
            'nombre', 
            'tipo', 
            'especificaciones', 
            'precio', 
            'estanteria'
        ]
        
    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        

#ProductoSolicitado

class ProductoSolicitadoSerializer(serializers.ModelSerializer):
    producto = serializers.SlugRelatedField(
        slug_field='codigo_barras',  # ← Usar código de barras en lugar de ID
        queryset=Producto.objects.all()
    )
    class Meta:
        model = ProductoSolicitado
        fields = ['producto', 'cantidad']



#Pedido

class PedidoCreateSerializer(serializers.ModelSerializer):
    # class Meta:
    #     model = Pedido
    #     fields = ['cliente'] 
    # def __init__(self, *args, **kwargs):
    #     self.usuario = kwargs.pop('usuario', None)
    #     super().__init__(*args, **kwargs)
    items = serializers.SlugRelatedField(
        many=True, 
        slug_field='sku',
        queryset=Item.objects.all()
    )
    productos_solicitados = ProductoSolicitadoSerializer(many=True, required=False)
    
    
    class Meta:
        model = Pedido
        fields = ['cliente', 'estado', 'items', 'operario', 'productos_solicitados']

    def validate(self, attrs):
        operario_login = attrs.get('operario')
        if not operario_login:
            raise serializers.ValidationError({'operario': 'El login del operario es requerido'})

        # TODO: Validar operario contra el microservicio de usuarios cuando el endpoint esté disponible
        # operario_data = obtener_operario(operario_login)
        # if not operario_data:
        #     raise serializers.ValidationError({'operario': 'Operario no encontrado en el microservicio de usuarios'})

        return attrs
    
    def create(self, validated_data):
        productos_solicitados_data = validated_data.pop('productos_solicitados', [])
        items_data = validated_data.pop('items', [])
        
        pedido = Pedido.objects.create(**validated_data)
        
        if items_data:
            pedido.items.set(items_data)
        
        for producto_data in productos_solicitados_data:
            ProductoSolicitado.objects.create(pedido=pedido, **producto_data)

        pedido.hash_de_integridad = pedido.generar_hash()
        pedido.save(update_fields=['hash_de_integridad'])
        
        return pedido
    

class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = '__all__'


class PedidoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ['estado','operario'] 
    #No puse que se pueda modificar los items porque a priori como esa info se supone que nos llega de la base de datos del ERP no debería poder
    #cambiarse el pedido fuera del estado en el que esta y el operario que lo esta atendiendo.

