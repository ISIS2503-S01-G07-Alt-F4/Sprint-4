from Pedido.logic.logic_inventario import (
    get_bodega,
    get_items_disponibles_por_producto,
    get_producto,
)
from Pedido.logic.logic_factura import crear_factura_para_pedido
from Pedido.logic.logic_usuario import verificar_permiso_rol, obtener_operario
from Pedido.logic.logic_auditoria import enviar_evento_auditoria
from Pedido.models import Pedido
from Pedido.serializers import PedidoCreateSerializer, PedidoSerializer
from rest_framework import status
from rest_framework.response import Response


def obtener_pedido(id : int):
    try:
        pedido = Pedido.objects.get(id = id)
        return pedido
    except Pedido.DoesNotExist:
        return None
    

def registrar_pedido(data: dict) -> Pedido:
    pedido = Pedido.objects.create(**data)
    return pedido



def procesar_creacion_pedido_completa(request):
    """
    Procesa la creación completa de un pedido desde la API
    Requiere autenticación vía token y permisos de JefeBodega
    """
    try:
        request_data = request.data
        user_data = getattr(request, 'user_data', None)
        
        # Verificar permisos (JefeBodega puede crear pedidos)
        tiene_permisos, mensaje = verificar_permiso_rol(user_data, ['JefeBodega'])
        if not tiene_permisos:
            return Response({
                'error': mensaje,
                'codigo': 'INSUFFICIENT_PERMISSIONS'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Preparar encabezados con el mismo token recibido
        auth_header = request.headers.get('Authorization')
        inv_headers = {'Authorization': auth_header} if auth_header else None

        # Validar datos del producto (pasando headers para inventario)
        pedido_data, campos_faltantes = validar_datos_pedido(request_data, inv_headers)
        
        if campos_faltantes != []:
            # Determinar el tipo de error
            error_msg = campos_faltantes[0]
            if "stock" in error_msg.lower() or "no existen" in error_msg.lower() or "no coinciden" in error_msg.lower() or "no pertenecen" in error_msg.lower():
                codigo = 'INVENTORY_ERROR'
            else:
                codigo = 'MISSING_FIELDS'
            
            return Response({'error': error_msg, 'codigo': codigo, 'campos_faltantes': campos_faltantes}, status=status.HTTP_400_BAD_REQUEST)
        
        print("Llega hasta acá")
        #Crear pedido
        success_response, error_response = crear_pedido_logica(pedido_data, user_data)
        if error_response:
            return error_response
        return success_response
        
    except Exception as e:
        print("Excepcion 1")
        return Response({'error': f'Error interno del servidor: {str(e)}','codigo': 'INTERNAL_ERROR'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


def crear_pedido_logica(pedido_data, user_data):
    """
    Lógica principal para crear un producto usando los serializers
    """
    try:
        # Crear el serializer con el usuario para validacionesp
        print(f"Datos recibidos para crear pedido: {pedido_data}")
        serializer = PedidoCreateSerializer(data=pedido_data)
        print("Puede crear el serializer")
        if serializer.is_valid():
            # Crear el pedido
            pedido = serializer.save()
            # Audit: creación de pedido
            enviar_evento_auditoria(
                user_data,
                action="CREATE",
                entity="PEDIDO",
                entity_id=pedido.id,
                description=f"Pedido creado por {user_data.get('username','usuario')}",
                metadata={"estado": pedido.estado, "items": list(pedido.items or [])}
            )
            # Serializar la respuesta con información completa
            response_serializer = PedidoSerializer(pedido)
            return Response({'mensaje': 'Pedido creado exitosamente', 'pedido': response_serializer.data, 'codigo': 'SUCCESS'}, status=status.HTTP_201_CREATED), None
        else:
            return None, Response({'error': 'Datos inválidos','errores': serializer.errors,'codigo': 'VALIDATION_ERROR'}, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        print("Excepción 2")
        return None, Response({'error': f'Error interno del servidor: {str(e)}','codigo': 'INTERNAL_ERROR'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def validar_datos_pedido(request_data, inv_headers=None):
    """Valida que los datos del pedido sean consistentes usando el microservicio de inventario."""

    bodega_seleccionada_id = request_data.get('bodega_seleccionada')
    items_ids = request_data.get('items') or []
    productos_request = request_data.get('productos_solicitados')

    campos_faltantes = []
    if not request_data.get('cliente'):
        campos_faltantes.append('cliente')
    if not request_data.get('operario'):
        campos_faltantes.append('operario')
    if not bodega_seleccionada_id:
        campos_faltantes.append('bodega_seleccionada')
    if not productos_request:
        campos_faltantes.append('productos_solicitados')

    if campos_faltantes:
        return None, campos_faltantes

    if not isinstance(productos_request, list):
        return None, ["'productos_solicitados' debe ser una lista"]

    productos_solicitados_data = []
    for idx, ps in enumerate(productos_request):
        producto_codigo = str(ps.get('producto', '')).strip()
        if not producto_codigo:
            return None, [f"El campo 'producto' es requerido en la posición {idx}"]

        try:
            cantidad = int(ps.get('cantidad', 0))
        except (TypeError, ValueError):
            return None, [f"La cantidad del producto {producto_codigo} debe ser numérica"]

        if cantidad <= 0:
            return None, [f"La cantidad del producto {producto_codigo} debe ser mayor a cero"]

        productos_solicitados_data.append({
            'producto': producto_codigo,
            'cantidad': cantidad
        })

    pedido_data = {
        'cliente': request_data.get('cliente'),
        'items': items_ids,
        'operario': request_data.get('operario'),
        'productos_solicitados': productos_solicitados_data,
        'bodega_id': str(bodega_seleccionada_id).strip(),
    }

    # Validar bodega
    bodega_data = get_bodega(bodega_seleccionada_id, headers=inv_headers)
    if not bodega_data:
        return None, [f"Bodega con ID {bodega_seleccionada_id} no existe"]

    # Validar productos y disponibilidad
    for producto in productos_solicitados_data:
        producto_codigo = producto['producto']
        producto_data = get_producto(producto_codigo, headers=inv_headers)
        if not producto_data:
            return None, [f"Producto con código {producto_codigo} no existe"]

        inventario_items = get_items_disponibles_por_producto(
            producto_codigo,
            bodega_seleccionada_id,
            headers=inv_headers
        )

        if inventario_items is None:
            return None, [
                f"No fue posible validar la disponibilidad del producto {producto_codigo} en la bodega {bodega_seleccionada_id}"
            ]

        disponibles = len(inventario_items)
        if disponibles < producto['cantidad']:
            return None, [
                f"No hay suficientes items disponibles del producto {producto_codigo} en la bodega {bodega_seleccionada_id}. "
                f"Solicitado {producto['cantidad']}, disponibles {disponibles}"
            ]

    return pedido_data, []


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
    Requiere autenticación y permisos según el estado destino
    """
    try:
        request_data = request.data
        user_data = getattr(request, 'user_data', None)
        
        
        # Obtener datos
        pedido_id = request_data.get('pedido_id')
        nuevo_estado = request_data.get('nuevo_estado')
        datos_factura = request_data.get('datos_factura')

        
        if not pedido_id or not nuevo_estado:
            return Response({
                'error': 'pedido_id y nuevo_estado son requeridos',
                'codigo': 'MISSING_FIELDS'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if nuevo_estado == "Empacado x despachar":            
            # Verificar permisos (Vendedor puede cambiar a Empacado x despachar)
            tiene_permisos, mensaje = verificar_permiso_rol(user_data, ['Vendedor'])
            if not tiene_permisos:
                return Response({
                    'error': mensaje,
                    'codigo': 'INSUFFICIENT_PERMISSIONS'
                }, status=status.HTTP_403_FORBIDDEN)
            
            if not datos_factura:
                return Response({
                    'error': 'Se requieren datos_factura cuando el nuevo estado es "Empacado x despachar"',
                    'codigo': 'FACTURA_DATA_REQUIRED'
                }, status=status.HTTP_400_BAD_REQUEST)
            pedido = Pedido.objects.get(id=pedido_id)
            # Validar campos requeridos de la factura
            campos_factura_requeridos = ['costo_total', 'metodo_pago', 'num_cuenta', 'comprobante']
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

        # Verificar permisos para otros cambios de estado
        tiene_permisos, mensaje = verificar_permiso_rol(user_data, ['JefeBodega', 'Operario', 'Vendedor'])
        if not tiene_permisos:
            return Response({
                'error': mensaje,
                'codigo': 'INSUFFICIENT_PERMISSIONS'
            }, status=status.HTTP_403_FORBIDDEN)

        # Aplicar cambio de estado
        pedido = Pedido.objects.get(id=pedido_id)
        estado_anterior = pedido.estado
        pedido.estado = nuevo_estado
        pedido.save()

        # Audit: actualización de estado de pedido
        enviar_evento_auditoria(
            user_data,
            action="UPDATE",
            entity="PEDIDO",
            entity_id=pedido.id,
            description=f"Estado de pedido actualizado de '{estado_anterior}' a '{nuevo_estado}' por {user_data.get('username','usuario')}",
            metadata={
                "estado_anterior": estado_anterior,
                "nuevo_estado": nuevo_estado,
                "usuario": user_data.get('username')
            }
        )
        
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
        user_data = getattr(request, 'user_data', None)
        
        # Verificar permisos (JefeBodega puede consultar)
        tiene_permisos, mensaje = verificar_permiso_rol(user_data, ['JefeBodega'])
        if not tiene_permisos:
            return Response({
                'mensaje': mensaje,
                'codigo': 'INSUFFICIENT_PERMISSIONS'
            }, status=status.HTTP_403_FORBIDDEN)
        
        pedido = Pedido.objects.get(id=id_pedido)

        if pedido:
            verificado = pedido.verificar_integridad()
            if verificado:
                serializer = PedidoSerializer(pedido)
                # Audit: lectura/consulta de pedido
                enviar_evento_auditoria(
                    user_data,
                    action="READ",
                    entity="PEDIDO",
                    entity_id=pedido.id,
                    description="Consulta de pedido",
                    metadata={"estado": pedido.estado}
                )
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

    

