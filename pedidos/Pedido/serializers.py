from rest_framework import serializers
from .models import Cliente, Pedido, ProductoSolicitado


class ProductoSolicitadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoSolicitado
        fields = ['producto', 'cantidad']


class PedidoCreateSerializer(serializers.ModelSerializer):
    items = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    productos_solicitados = ProductoSolicitadoSerializer(many=True, required=False)
    
    
    class Meta:
        model = Pedido
        fields = ['cliente', 'estado', 'items', 'operario', 'bodega_id', 'productos_solicitados']

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

        pedido = Pedido.objects.create(items=items_data, **validated_data)
        
        for producto_data in productos_solicitados_data:
            ProductoSolicitado.objects.create(pedido=pedido, **producto_data)

        pedido.hash_de_integridad = pedido.generar_hash()
        pedido.save(update_fields=['hash_de_integridad'])
        
        return pedido
    

class PedidoSerializer(serializers.ModelSerializer):
    productos_solicitados = ProductoSolicitadoSerializer(many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = '__all__'


class PedidoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ['estado','operario'] 
    #No puse que se pueda modificar los items porque a priori como esa info se supone que nos llega de la base de datos del ERP no debería poder
    #cambiarse el pedido fuera del estado en el que esta y el operario que lo esta atendiendo.

