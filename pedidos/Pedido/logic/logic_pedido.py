from Pedido.logic.logic_api import autenticar_usuario_api
from Pedido.logic.logic_inventario import get_item, get_bodega
from Pedido.logic.logic_factura import crear_factura_para_pedido
from Pedido.models import Pedido
from django.contrib.auth import authenticate
from Pedido.serializers import PedidoCreateSerializer, PedidoSerializer
from rest_framework import status
from rest_framework.response import Response

from Users.logic.logic_usuario import token_requerido


def obtener_pedido(id : int):
    try:
        pedido = Pedido.objects.get(id = id)
        return pedido
    except Pedido.DoesNotExist:
        return None
    

def registrar_pedido(data: dict) -> Pedido:
    pedido = Pedido.objects.create(**data)
    return pedido


def verificar_permisos_pedido(usuario):
    """
    Verifica si el usuario tiene permisos para crear pedidos
    """
    # if not usuario.is_authenticated:
    #     return False, "Usuario no autenticado"
    
    if usuario.rol not in ['JefeBodega']:
        return False, "No tienes permisos para crear pedidos"
    
    return True, "OK"


def procesar_creacion_pedido_completa(request):
    """
    Procesa la creación completa de un pedido desde la API
    Coherente con el sistema de autenticación usado en las vistas web
    """
    try:
        # 1. Autenticar usuario usando username/password en el body (como en las vistas web)
        # username = request_data.get('username')
        # password = request_data.get('password')
        
        # user, error_response = autenticar_usuario_api(username, password)
        # if error_response:
        #     return error_response
        request_data = request.data
        user = request.user
        
        # 2. Verificar permisos
        tiene_permisos, mensaje = verificar_permisos_pedido(user)
        if not tiene_permisos:
            return Response({'error': mensaje,'codigo': 'INSUFFICIENT_PERMISSIONS'}, status=status.HTTP_403_FORBIDDEN)

    
        # 3. Validar datos del producto
        pedido_data, campos_faltantes = validar_datos_pedido(request_data)
        
        if campos_faltantes != []:
            return Response({'error': f'Campos requeridos faltantes: {", ".join(campos_faltantes)}','codigo': 'MISSING_FIELDS','campos_faltantes': campos_faltantes}, status=status.HTTP_400_BAD_REQUEST)
        
        print("Llega hasta acá")
        # 4. Crear pedido
        success_response, error_response = crear_pedido_logica(user, pedido_data)
        if error_response:
            return error_response
        return success_response
        
    except Exception as e:
        print("Excepcion 1")
        return Response({'error': f'Error interno del servidor: {str(e)}','codigo': 'INTERNAL_ERROR'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


def crear_pedido_logica(usuario, pedido_data):
    """
    Lógica principal para crear un producto usando los serializers
    """
    try:
        # Crear el serializer con el usuario para validaciones
        print(f"Datos recibidos para crear pedido: {pedido_data}")
        serializer = PedidoCreateSerializer(data=pedido_data)
        print("Puede crear el serializer")
        if serializer.is_valid():
            # Crear el pedido
            pedido = serializer.save()
            # Serializar la respuesta con información completa
            response_serializer = PedidoSerializer(pedido)
            return Response({'mensaje': 'Pedido creado exitosamente', 'pedido': response_serializer.data, 'codigo': 'SUCCESS'}, status=status.HTTP_201_CREATED), None
        else:
            return None, Response({'error': 'Datos inválidos','errores': serializer.errors,'codigo': 'VALIDATION_ERROR'}, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        print("Excepción 2")
        return None, Response({'error': f'Error interno del servidor: {str(e)}','codigo': 'INTERNAL_ERROR'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def validar_datos_pedido(request_data):
    """
    Valida que todos los campos requeridos estén presentes
    """
   
    bodega_seleccionada_id = request_data.get('bodega_seleccionada')
    items_ids = request_data.get('items', [])
    
    skus_unicos = set()
    skus_repetidos = set()
    
    for sku in items_ids:
        if sku in skus_unicos:
            skus_repetidos.add(sku)
        else:
            skus_unicos.add(sku)
    
    if skus_repetidos:
        return None, [f"SKUs repetidos no permitidos: {', '.join(skus_repetidos)}"]
    
    productos_solicitados_data = []
    for ps in request_data.get('productos_solicitados', []):
        productos_solicitados_data.append({
            'producto': ps['producto'],  # ← código de barras (string)
            'cantidad': int(ps['cantidad'])  # ← cantidad sigue siendo int
        })
    pedido_data = {
        'cliente': request_data.get('cliente'),
        'items': items_ids,
        'operario': request_data.get('operario'),
        'productos_solicitados': productos_solicitados_data,
        'bodega_seleccionada': bodega_seleccionada_id
    }
    if items_ids and productos_solicitados_data:
        # 1. Verificar misma cantidad
        if len(items_ids) != len(productos_solicitados_data):
            return None, [f"La cantidad de items ({len(items_ids)}) no coincide con la cantidad de productos solicitados ({len(productos_solicitados_data)})"]
        
        # 2. Obtener los productos de los items
        try:
            items_productos = {}
            skus_no_encontrados = []
            
            for sku in items_ids:
                item_data = get_item(sku)
                if item_data:
                    items_productos[sku] = item_data['producto_id']
                else:
                    skus_no_encontrados.append(sku)
            
            # 3. Verificar que todos los SKUs existen
            if skus_no_encontrados:
                return None, [f"Los siguientes SKUs no existen: {', '.join(skus_no_encontrados)}"]
            
            # 4. Verificar coincidencia de productos
            productos_no_coincidentes = []
            for i, item_sku in enumerate(items_ids):
                producto_solicitado_codigo = productos_solicitados_data[i]['producto']
                producto_item_codigo = items_productos[item_sku]
                
                if producto_item_codigo != producto_solicitado_codigo:
                    productos_no_coincidentes.append({
                        'item_sku': item_sku,
                        'producto_item': producto_item_codigo,
                        'producto_solicitado': producto_solicitado_codigo
                    })
            
            if productos_no_coincidentes:
                error_msg = "Los productos de los items no coinciden con los productos solicitados:"
                for error in productos_no_coincidentes:
                    error_msg += f"\n- Item SKU {error['item_sku']} tiene producto {error['producto_item']} pero se solicitó {error['producto_solicitado']}"
                return None, [error_msg]
                
        except Exception as e:
            return None, [f"Error validando coincidencia de productos: {str(e)}"]
    # Validar que los items estén en la bodega seleccionada
    if bodega_seleccionada_id and items_ids:
        try:
            bodega_data = get_bodega(bodega_seleccionada_id)
            if not bodega_data:
                 return None, [f"Bodega con ID {bodega_seleccionada_id} no existe"]
            
            # Verificar cada item
            items_fuera_de_bodega = []
            for item_id in items_ids:
                item_data = get_item(item_id)
                if not item_data:
                     return None, [f"Item con SKU {item_id} no existe"]
                
                if item_data.get('bodega_id') != bodega_seleccionada_id:
                        actual_bodega = get_bodega(item_data.get('bodega_id'))
                        actual_bodega_name = actual_bodega.get('ciudad', 'Desconocida') if actual_bodega else 'Desconocida'
                        
                        items_fuera_de_bodega.append({
                            'item_id': item_id,
                            'producto': item_data.get('producto_id'),
                            'bodega_actual': actual_bodega_name
                        })
            
            if items_fuera_de_bodega:
                error_msg = "Algunos items no pertenecen a la bodega seleccionada:"
                for item_error in items_fuera_de_bodega:
                    error_msg += f"\n- Item {item_error['item_id']} ({item_error['producto']}) está en {item_error['bodega_actual']}"
                return None, [error_msg]
                
        except Exception as e:
            return None, [f"Error validando bodega: {str(e)}"]
    
    campos_requeridos = ['cliente', 'items','operario','productos_solicitados', 'bodega_seleccionada']  
    campos_faltantes = []
    
    for campo in campos_requeridos:
        if not pedido_data.get(campo):
            campos_faltantes.append(campo)    
            
    return pedido_data, campos_faltantes


def actualizar_estado_pedido(pedido_id, nuevo_estado):
    """
    Actualiza el estado de un pedido usando la instancia
    """
    try:
        pedido = Pedido.objects.get(id=pedido_id)
        
        # Validar transición de estado (opcional)
        #Esto hay que usarlo eventualmente porque no debería de poder pasar un pedido
        #de Alistamiento de una vez a Verificado, pero para efectos de la experimentación
        #es suficiente permitir solo el cambio de estado
        # estados_permitidos = {
        #     'Alistamiento': ['Por verificar', 'Anulado'],
        #     'Por verificar': ['Verificado', 'Rechazado x verificar'],
        #     'Verificado': ['Empacado x despachar'],
        # }
        
        # estado_actual = pedido.estado
        # if (estados_permitidos.get(estado_actual) and 
        #     nuevo_estado not in estados_permitidos[estado_actual]):
        #     return None, f"Transición no permitida de {estado_actual} a {nuevo_estado}"
        
        # Actualizar y guardar
        pedido.estado = nuevo_estado
        pedido.save()
        
        return pedido, None
        
    except Pedido.DoesNotExist:
        return None, "Pedido no encontrado"
    except Exception as e:
        return None, f"Error actualizando pedido: {str(e)}"
    

def actualizar_estado_pedido_api(request):
    """
    Endpoint para actualizar estado desde API
    """
    try:
        # Autenticación
        # username = request_data.get('username')
        # password = request_data.get('password')
        
        # user, error_response = autenticar_usuario_api(username, password)
        # if error_response:
        #     return error_response
        request_data = request.data
        user = request.user
        
        
        # Obtener datos
        pedido_id = request_data.get('pedido_id')
        nuevo_estado = request_data.get('nuevo_estado')
        datos_factura = request_data.get('datos_factura')

        
        if not pedido_id or not nuevo_estado:
            return Response({
                'error': 'pedido_id y nuevo_estado son requeridos',
                'codigo': 'MISSING_FIELDS'
            }, status=status.HTTP_400_BAD_REQUEST)
            pedido = Pedido.objects.get(id=pedido_id)
            cliente_id = pedido.cliente.id

        
        if nuevo_estado == "Empacado x despachar":
            # Verificar permisos
            if not permiso_actualizar_pedido_empacado_x_despachar(user):
                return Response({
                    'error': 'No tienes permisos para actualizar pedidos',
                    'codigo': 'INSUFFICIENT_PERMISSIONS'
                }, status=status.HTTP_403_FORBIDDEN)
            
            if not datos_factura:
                return Response({
                    'error': 'Se requieren datos_factura cuando el nuevo estado es "Empacado x despachar"',
                    'codigo': 'FACTURA_DATA_REQUIRED'
                }, status=status.HTTP_400_BAD_REQUEST)
            pedido = Pedido.objects.get(id=pedido_id)
            # Validar campos requeridos de la factura
            campos_factura_requeridos = [ 'metodo_pago', 'num_cuenta', 'comprobante']
            campos_faltantes = [campo for campo in campos_factura_requeridos if not datos_factura.get(campo)]
            
            
            if campos_faltantes:
                return Response({
                    'error': f'Campos faltantes en datos_factura: {", ".join(campos_faltantes)}',
                    'codigo': 'MISSING_FACTURA_FIELDS'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            factura, error_factura = crear_factura_para_pedido(pedido, datos_factura)
            
            if error_factura:
                return Response({
                    'error': error_factura,
                    'codigo': 'FACTURA_CREATION_ERROR'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            pedido.factura = factura
            pedido.save()

        # Verificar permisos
        if not permiso_actualizar_pedido(user):
            return Response({
                'error': 'No tienes permisos para actualizar pedidos',
                'codigo': 'INSUFFICIENT_PERMISSIONS'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Actualizar
        pedido, error = actualizar_estado_pedido(pedido_id, nuevo_estado)
        
        if error:
            return Response({
                'error': error,
                'codigo': 'UPDATE_ERROR'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Serializar respuesta
        serializer = PedidoSerializer(pedido)
        return Response({
            'mensaje': 'Estado actualizado exitosamente',
            'pedido': serializer.data,
            'codigo': 'SUCCESS'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Error interno del servidor: {str(e)}',
            'codigo': 'INTERNAL_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def permiso_actualizar_pedido(usuario):
    """
    Verifica si el usuario puede actualizar pedidos
    """
    roles_permitidos = [ 'JefeBodega','Operario','Vendedor']
    return usuario.rol in roles_permitidos

def permiso_actualizar_pedido_empacado_x_despachar(usuario):
    """
    Verifica si el usuario puede actualizar pedidos
    """
    roles_permitidos = [ 'Vendedor']
    return usuario.rol in roles_permitidos

def verificar_integridad_pedido(request_data):
    """
    Verifica la integrudad de un pedido
    """
    pedido_id = request_data.get('pedido_id')
    if not pedido_id :
            return Response({
                'error': 'pedido_id es requerido',
                'codigo': 'MISSING_FIELDS'
            }, status=status.HTTP_400_BAD_REQUEST)
    pedido = Pedido.objects.get(id=pedido_id)
    if pedido:
        print("entro a donde era")
        return pedido.verificar_integridad()
    else:
        print("entro al else")
        return False
    
def consultar_pedido_por_id(request, id_pedido):
    try:
        user = request.user
        if user.rol not in ['JefeBodega']:
            return Response({
                    'mensaje': 'No tienes los permisos suficientes para consultar pedidos.',
                    'codigo': 'PERMISOS_VULNERADOS'
                }, status=status.HTTP_409_CONFLICT)
        pedido = Pedido.objects.get(id=id_pedido)

        if pedido:
            verificado = pedido.verificar_integridad()
            if verificado:
                serializer = PedidoSerializer(pedido)
                return Response({
                    'mensaje': 'Estado actualizado exitosamente',
                    'pedido': serializer.data,
                    'codigo': 'SUCCESS'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'mensaje': 'El pedido ha sido modificado o vulnerado.',
                    'codigo': 'VULNERADO'
                }, status=status.HTTP_409_CONFLICT)
        else:
            return Response({
                'mensaje': f'No se encontró el pedido con id {id_pedido}.',
                'codigo': 'NOT_FOUND'
            }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({
            'error': f'Error interno del servidor: {str(e)}',
            'codigo': 'INTERNAL_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    

