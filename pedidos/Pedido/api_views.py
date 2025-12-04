from Pedido.logic.logic_pedido import actualizar_estado_pedido_api, consultar_pedido_por_id, procesar_creacion_pedido_completa, verificar_integridad_pedido
from Pedido.logic.logic_usuario import token_requerido
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

from Users.logic.logic_usuario import token_requerido

from .logic.logic_api import procesar_creacion_producto_completa


@api_view(['POST'])
@permission_classes([AllowAny]) 
@csrf_exempt
@token_requerido
def crear_producto_api(request):
    """
    Endpoint para crear un nuevo producto
    
    Parámetros requeridos en el body JSON:
    - username: Usuario para autenticación
    - password: Contraseña para autenticación
    - codigo_barras: Código único del producto
    - nombre: Nombre del producto
    - tipo: Tipo de producto
    - especificaciones: Especificaciones técnicas
    - precio: Precio del producto
    - estanteria: ID de la estantería donde se ubicará
    - bodega_seleccionada (opcional): ID de la bodega para operarios
    
    Ejemplo de request:
    {
        "username": "operario1",
        "password": "password123",
        "codigo_barras": "1234567890123",
        "nombre": "Chaqueta de Prueba",
        "tipo": "Prueba",
        "especificaciones": "Chaqueta de prueba, talla M, color rojo",
        "precio": "1500000.00",
        "estanteria": 1,
        "bodega_seleccionada": 2 # Solo para operarios
    }
    """
    return procesar_creacion_producto_completa(request.data)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@token_requerido
def crear_pedido_api(request):
    """
    Endpoint para crear un nuevo pedido
    
    Parámetros requeridos en el body JSON:
    - username: Usuario para autenticación
    - password: Contraseña para autenticación
    - Bodega_seleccionada: Es el id de la bodega a la que se le remite el pedido
    - cliente: Id del cliente relacionado con el pedido
    - operario: login del operario al que se le asigna el pedido
    - items: una lista de los SKU de los items del pedido
    - productos_solicitados: una lista en formato json donde cada elemento tiene el id del producto
      junto con la cantidad pedida de dicho producto. Sobra decir que tiene que ser la misma cantidad
      de productos_solicitados que de items.
    
    Ejemplo de request:
    {
        "username": "operario1",
        "password": "password123",
        "bodega_seleccionada": 1
        "cliente" : 1,
        "operario" : "Joao",
        "items":[1,2,3],
        "productos_solicitados":
        {
            {
                "producto":1,
                "cantidad":2
            },
            {
                "producto":2,
                "cantidad":3
            },
            {
                "producto":3,
                "cantidad":4
            }
        }

    }
    """
    return procesar_creacion_pedido_completa(request)


@csrf_exempt
@api_view(['PUT'])
@permission_classes([AllowAny])
@token_requerido
def cambiar_estado_pedido_api(request, id):
    """
    Endpoint para crear un nuevo pedido
    
    Parámetros requeridos en el body JSON:
    - username: Usuario para autenticación
    - password: Contraseña para autenticación
    - nuevo_estado: El estado al que se quiere cambiar el pedido
    - pedido_id: El id del pedido cuyo estado se quiere modificar
    - datos_factura: Esto es opcional, y debe aparecer unicamente si el estado al que se quiere cambiar el pedido es Empacado x despachar
    Tiene información del metodo de pago, numero de cuenta y comprobante. Si el nuevo estado es diferente a Empacado x despachar, esta parte
    se puede omitir.
    
    Ejemplo de request:
    {
        "username": "operario1",
        "password": "password123",
        "nuevo_estado":"Rechazado x verificar",
        "pedido_id" : 1,
        "datos_factura": 
        {
            "metodo_pago": "Tarjeta",
            "num_cuenta": "123456789", 
            "comprobante": "COMP-001"
        }

    }
    """
    # Inyectar id de ruta si no viene en el body
    if isinstance(request.data, dict) and 'pedido_id' not in request.data:
        request.data['pedido_id'] = id
    return actualizar_estado_pedido_api(request)

@api_view(['GET'])
def health_check(request):
    return Response({"status": "ok"}, status=200)

@api_view(['GET'])
@token_requerido
def verificar_integridad(request):
    return Response(verificar_integridad_pedido(request.data))


@api_view(['GET'])
@token_requerido
def consultar_pedido(request, id):
    return consultar_pedido_por_id(request, id)
