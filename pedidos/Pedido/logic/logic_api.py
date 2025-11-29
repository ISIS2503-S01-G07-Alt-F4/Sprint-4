"""
Lógica de negocio para la API de productos
Coherente con el patrón de autenticación usado en el sistema
"""
import time
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response

from Pedido.models import Producto, Estanteria
from Pedido.serializers import ProductoCreateSerializer, ProductoSerializer
from Pedido.logic.logic_bodega import get_bodegas_operario
from Users.models import Usuario


def autenticar_usuario_api(username, password):
    """
    Autentica un usuario para la API usando el sistema de autenticación de Django
    con caché para mejorar el rendimiento
    
    Returns:
        tuple: (user_object, error_response)
        Si hay error, user_object será None y error_response contendrá la respuesta de error
    """
    if not username or not password:
        return None, Response({'error': 'Se requieren username y password para la autenticación'}, status=status.HTTP_400_BAD_REQUEST)
    
    cache_key = f'user_auth_{username}'
    
    # Intentar obtener usuario del cache
    login_en_cache = cache.get(cache_key)
    
    if login_en_cache:
        # Usuario encontrado en cache
        try:
            user_model = get_user_model()
            user = user_model.objects.get(id=login_en_cache)
            return user, None
        except user_model.DoesNotExist:
            cache.delete(cache_key)
    
    # Usuario no está en cache, se autentica normal
    user = authenticate(username=username, password=password)
    if not user:
        return None, Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Guardar usuario en cache por 5 minutos
    cache.set(cache_key, user.id, timeout=300)
    
    return user, None


def verificar_permisos_producto(usuario):
    """
    Verifica si el usuario tiene permisos para crear productos
    """
    if not usuario.is_authenticated:
        return False, "Usuario no autenticado"
    
    if usuario.rol not in ['JefeBodega', 'Operario']:
        return False, "No tienes permisos para crear productos"
    
    return True, "OK"


def obtener_estanterias_usuario(usuario, bodega_seleccionada_id=None):
    """
    Obtiene las estanterías disponibles para el usuario según su rol y bodega
    """
    if usuario.rol == 'JefeBodega' and hasattr(usuario, 'jefebodega'):
        bodega = usuario.jefebodega.bodega
        return Estanteria.objects.filter(bodega=bodega)
    elif usuario.rol == 'Operario' and hasattr(usuario, 'operario'):
        if bodega_seleccionada_id:
            # Verificar que la bodega pertenezca al operario
            bodegas_operario = get_bodegas_operario(usuario)
            if bodegas_operario.filter(id=bodega_seleccionada_id).exists():
                return Estanteria.objects.filter(bodega_id=bodega_seleccionada_id)
        else:
            # Si no hay bodega seleccionada, mostrar todas las estanterías de sus bodegas
            bodegas_operario = get_bodegas_operario(usuario)
            return Estanteria.objects.filter(bodega__in=bodegas_operario)
    
    return Estanteria.objects.none()


def validar_datos_producto(request_data):
    """
    Valida que todos los campos requeridos estén presentes
    """
    producto_data = {
        'codigo_barras': request_data.get('codigo_barras'),
        'nombre': request_data.get('nombre'),
        'tipo': request_data.get('tipo'),
        'especificaciones': request_data.get('especificaciones'),
        'precio': request_data.get('precio'),
        'estanteria': request_data.get('estanteria')
    }
    
    campos_requeridos = ['codigo_barras', 'nombre', 'tipo', 'especificaciones', 'precio', 'estanteria']
    campos_faltantes = []
    
    for campo in campos_requeridos:
        if not producto_data.get(campo):
            campos_faltantes.append(campo)    
            
    return producto_data, campos_faltantes


def validar_estanteria_acceso(estanteria_id, usuario, bodega_seleccionada_id=None):
    """
    Valida que la estantería existe y el usuario tiene acceso a ella
    """
    try:
        estanteria_id = int(estanteria_id)
        estanteria = Estanteria.objects.get(id=estanteria_id)
    except (ValueError, Estanteria.DoesNotExist):
        return None, Response({'error': 'Estantería no válida o no encontrada'}, status=status.HTTP_400_BAD_REQUEST)

    # Verificar acceso a la estantería según el rol del usuario
    estanterias_disponibles = obtener_estanterias_usuario(usuario, bodega_seleccionada_id)
    if not estanterias_disponibles.filter(id=estanteria_id).exists():
        return None, Response({'error': 'No tienes acceso a esta estantería o bodega'}, status=status.HTTP_403_FORBIDDEN)
    return estanteria, None


def crear_producto_logica(usuario, producto_data):
    """
    Lógica principal para crear un producto usando los serializers
    """
    try:
        # Crear el serializer con el usuario para validaciones
        serializer = ProductoCreateSerializer(data=producto_data, usuario=usuario)
        if serializer.is_valid():
            # Crear el producto
            producto = serializer.save()
            # Serializar la respuesta con información completa
            response_serializer = ProductoSerializer(producto)
            return Response({'mensaje': 'Producto creado exitosamente', 'producto': response_serializer.data}, status=status.HTTP_201_CREATED), None
        else:
            return None, Response({'error': 'Datos inválidos','errores': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return None, Response({'error': f'Error interno del servidor: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def procesar_creacion_producto_completa(request_data):
    """
    Procesa la creación completa de un producto desde la API
    Coherente con el sistema de autenticación usado en las vistas web
    """
    try:
        tiempo_inicio = time.time()
        # 1. Autenticar usuario 
        username = request_data.get('username')
        password = request_data.get('password')
        
        # user, error_response = autenticar_usuario_api(username, password)
        # if error_response:
        #     return error_response
        try:
            user = Usuario.objects.get(login=username)
            
        except Usuario.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado en sistema'}, status=404)
        
        tiempo_autenticacion = time.time() - tiempo_inicio
        
        # 2. Verificar permisos
        tiene_permisos, mensaje = verificar_permisos_producto(user)
        if not tiene_permisos:
            return Response({'error': mensaje}, status=status.HTTP_403_FORBIDDEN)
        tiempo_verificacion_permisos = time.time() - tiempo_inicio
        
        # 3. Validar datos del producto
        producto_data, campos_faltantes = validar_datos_producto(request_data)
        tiempo_validacion_datos = time.time() - tiempo_inicio
        if campos_faltantes != []:
            return Response({'error': f'Campos requeridos faltantes: {", ".join(campos_faltantes)}','campos_faltantes': campos_faltantes}, status=status.HTTP_400_BAD_REQUEST)
        
        # 4. Validar estantería y acceso
        bodega_seleccionada_id = request_data.get('bodega_seleccionada')
        _, error_response = validar_estanteria_acceso(producto_data['estanteria'], user, bodega_seleccionada_id)
        if error_response:
            return error_response
        tiempo_validacion_estanteria = time.time() - tiempo_inicio
        
        # 5. Crear producto
        success_response, error_response = crear_producto_logica(user, producto_data)
        if error_response:
            return error_response
        tiempo_creacion_producto = time.time() - tiempo_inicio
        return Response({
            'mensaje': 'Producto creado exitosamente',
            'producto': success_response.data.get('producto'),
            'tiempos': {
                'autenticacion': tiempo_autenticacion,
                'verificacion_permisos': tiempo_verificacion_permisos,
                'validacion_datos': tiempo_validacion_datos,
                'validacion_estanteria': tiempo_validacion_estanteria,
                'creacion_producto': tiempo_creacion_producto,
                'total': time.time() - tiempo_inicio
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': f'Error interno del servidor: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)