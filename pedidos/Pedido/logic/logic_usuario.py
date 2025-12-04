"""
Cliente HTTP para comunicarse con el microservicio de Usuarios
Este módulo maneja la autenticación y validación de permisos
contra el servicio externo de usuarios (vía Kong)
"""
import requests
import os
import jwt
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from functools import wraps

USERS_SERVICE_URL = getattr(settings, 'USERS_SERVICE_URL', 'http://usuarios:8081/usuarios')


def autenticar_usuario_api(username, password):
    """
    Autentica un usuario contra el microservicio de Usuarios
    
    Returns:
        tuple: (user_data_dict, error_response)
        Si hay error, user_data será None y error_response contendrá la respuesta de error
    """
    if not username or not password:
        return None, Response({
            'error': 'Se requieren username y password para la autenticación',
            'codigo': 'MISSING_CREDENTIALS'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Llamar al endpoint de autenticación del servicio de usuarios
        response = requests.post(
            f"{USERS_SERVICE_URL}/auth/login",
            json={'username': username, 'password': password},
            timeout=5
        )
        
        if response.status_code == 200:
            user_data = response.json()
            return user_data, None
        elif response.status_code == 401:
            return None, Response({
                'error': 'Credenciales inválidas',
                'codigo': 'INVALID_CREDENTIALS'
            }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return None, Response({
                'error': 'Error al autenticar con el servicio de usuarios',
                'codigo': 'AUTH_SERVICE_ERROR'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
    except requests.RequestException as e:
        return None, Response({
            'error': f'Servicio de usuarios no disponible: {str(e)}',
            'codigo': 'SERVICE_UNAVAILABLE'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


def validar_token(token):
    """
    Valida un token contra el microservicio de Usuarios.
    Si el microservicio no está disponible, valida directamente de Auth0 como fallback.
    
    Returns:
        tuple: (user_data_dict, error_response)
    """
    if not token:
        return None, Response({
            'error': 'Token no proporcionado',
            'codigo': 'MISSING_TOKEN'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Primero, intentar validar con el microservicio de usuarios
    try:
        response = requests.get(
            f"{USERS_SERVICE_URL}/auth/validate",
            headers={'Authorization': f'Bearer {token}'},
            timeout=5
        )
        
        if response.status_code == 200:
            user_data = response.json()
            return user_data, None
        elif response.status_code == 401:
            return None, Response({
                'error': 'Token inválido o expirado',
                'codigo': 'INVALID_TOKEN'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except requests.RequestException:
        # Fallback: si el microservicio de usuarios no está disponible, validar directamente de Auth0
        pass
    
    # Fallback: validar token directamente de Auth0
    try:
        jwks_url = f"https://{os.getenv('AUTHZ_DOMAIN')}/.well-known/jwks.json"
        jwks_client = jwt.PyJWKClient(jwks_url)
        
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=['RS256'],
            audience=[os.getenv('AUTHZ_AUDIENCE'), os.getenv('CLIENT_ID')],
            issuer=f"https://{os.getenv('AUTHZ_DOMAIN')}/"
        )
        
        # Extraer información del usuario del payload
        user_data = {
            'sub': payload.get('sub'),
            'username': payload.get('nickname'),
            'name': payload.get('name'),
            'email': payload.get('email'),
            'rol': 'JefeBodega'  # Por defecto, en el futuro se obtendrá del token o metadata
        }
        
        return user_data, None
        
    except jwt.ExpiredSignatureError:
        return None, Response({
            'error': 'Token expirado',
            'codigo': 'EXPIRED_TOKEN'
        }, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError as e:
        return None, Response({
            'error': f'Token inválido: {str(e)}',
            'codigo': 'INVALID_TOKEN'
        }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return None, Response({
            'error': f'Error validando token: {str(e)}',
            'codigo': 'VALIDATION_ERROR'
        }, status=status.HTTP_401_UNAUTHORIZED)


def token_requerido(view_func):
    """
    Decorador para requerir autenticación por token en endpoints
    Valida el token contra el microservicio de usuarios y adjunta user_data al request
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Extraer token del header Authorization
        auth_header = request.headers.get('Authorization', '')
        token = None
        
        if auth_header.startswith('Token '):
            token = auth_header[6:]
        elif auth_header.startswith('Bearer '):
            token = auth_header[7:]
        
        # Validar token contra servicio de usuarios
        user_data, error_response = validar_token(token)
        if error_response:
            return error_response
        
        # Adjuntar datos del usuario al request para uso posterior
        request.user_data = user_data
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def verificar_permiso_rol(user_data, roles_permitidos):
    """
    Verifica si el usuario tiene uno de los roles permitidos
    
    Args:
        user_data: diccionario con información del usuario (debe incluir 'rol')
        roles_permitidos: lista de roles que pueden ejecutar la acción
        
    Returns:
        tuple: (tiene_permiso: bool, mensaje: str)
    """
    if not user_data:
        return False, "Usuario no autenticado"
    
    rol_usuario = user_data.get('rol')
    if not rol_usuario:
        return False, "Usuario sin rol asignado"
    
    if rol_usuario not in roles_permitidos:
        return False, f"Se requiere uno de los siguientes roles: {', '.join(roles_permitidos)}"
    
    return True, "OK"


def obtener_operario(login_operario):
    """
    Obtiene información de un operario desde el microservicio de Usuarios
    
    Args:
        login_operario: identificador del operario
        
    Returns:
        dict o None: datos del operario si existe
    """
    try:
        response = requests.get(
            f"{USERS_SERVICE_URL}/operarios/{login_operario}",
            timeout=5
        )
        
        if response.status_code == 200:
            return response.json()
        return None
        
    except requests.RequestException:
        return None
