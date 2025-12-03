from functools import wraps
import os
import logging

import jwt
import requests
from django.http import JsonResponse
from django.contrib.auth import login, logout

from ..models import Usuario, JefeBodega, Operario, Vendedor
def get_usuarios():
    queryset = Usuario.objects.all()
    return (queryset)

def create_usuario(data):
    modelos = {
        'Usuario': Usuario,
        'JefeBodega': JefeBodega,
        'Operario': Operario,
        'Vendedor':Vendedor
    }
    modelo = modelos.get(data['rol'])
    
    
    try:
        datos_usuario = {
            'login': data['login'],
            'password': data['contraseña'],
            'nombre': data['nombre'],
            'apellido': data['apellido'],
            'rol': data['rol']
        }
        
        
        if data['rol'] == 'JefeBodega':
            # JefeBodega: tomar la primera bodega de la lista
            bodegas_seleccionadas = data.get('bodegas', [])
            if bodegas_seleccionadas:
                datos_usuario['bodega'] = bodegas_seleccionadas[0]
            usuario = modelo.objects.create_user(**datos_usuario)
            
        elif data['rol'] == 'Operario':
            usuario = modelo.objects.create_user(**datos_usuario)
            bodegas_seleccionadas = data.get('bodegas', [])
            if bodegas_seleccionadas:
                usuario.bodega.set(bodegas_seleccionadas) 
        elif data['rol'] == 'Vendedor':
            usuario = modelo.objects.create_user(**datos_usuario)
            bodegas_seleccionadas = data.get('bodegas', [])
            if bodegas_seleccionadas:
                usuario.bodega.set(bodegas_seleccionadas) 
        else:
            usuario = modelo.objects.create_user(**datos_usuario)
        crear_usuario_management_api(data['login'],data['contraseña'])
        print("Usuario creado correctamente")
        return usuario
        
    except Exception as e:
        print(f"Error creando usuario: {e}")
        return None


# def login_usuario(request, form):
#     login_info = form.cleaned_data['login']
#     password = form.cleaned_data['password']
#     usuario = authenticate(request, login=login_info, password=password) # Verificar si el usuario existe
    
#     if usuario is not None:
#         login(request, usuario) # Iniciar sesión del usuario y persistirlo en la sesión
#         return usuario
#     else:
#         return None
# def login_usuario(request, form):
#     username = form.cleaned_data['login']
#     password = form.cleaned_data['password']
    
#     url = f"https://dev-2huk2uien4i6jdxa.us.auth0.com/oauth/token"
#     data = {
#         "grant_type": "password",
#         "username": username,
#         "password": password,
#         "audience": "http://localhost:8000/api", 
#         "client_id": "rjAfrQ1Hy4hsvLn8GeUC4ZDtRyRtjsT6",
#         "client_secret": "_tr4RXV3PDlTMewwqd9nydsdznSbVsd0R8XFv33OgE57EWpJPqvsBrDYOHQZ7kHr",
#         "scope": "openid profile email"
#     }

#     response = requests.post(url, json=data)
   
#     if response.status_code == 200:
#         tokens = response.json()  
#         request.session['access_token'] = tokens['access_token']
#         request.session['id_token'] = tokens.get('id_token')
#         login(request, username)
#         return JsonResponse({"mensaje": "Login exitoso", "tokens": tokens})
#     else:
#         return JsonResponse({"error": "Credenciales inválidas", "detalles": response.text}, status=401)
    
logger = logging.getLogger(__name__)

def login_usuario(request, form):
    username = form.cleaned_data['login']
    password = form.cleaned_data['password']
    
    url = f"https://{os.getenv('AUTHZ_DOMAIN')}/oauth/token"
    #print(os.getenv('AUTHZ_AUDIENCE'))
    data = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "audience": f"{os.getenv('AUTHZ_AUDIENCE')}", 
        "client_id": f"{os.getenv('CLIENT_ID')}",
        "client_secret": f"{os.getenv('CLIENT_SECRET')}",
        "scope": "openid profile email",
        "realm": "Username-Password-Authentication"
        
    }
    logger.info("Antes del post")
    print("ANTES DEL POST")
    response = requests.post(url, json=data)
    print("STATUS:", response.status_code)
    print("RESPONSE TEXT:", response.text)
    print("DESPUES DEL POST")
    if response.status_code == 200:
        
        tokens = response.json()
        logger.info("LLego acá")
        print("LLEGO ACÁ")
        request.session['access_token'] = tokens['access_token']
        
        request.session['id_token'] = tokens.get('id_token')
       
        user = get_or_create_usuario(username=username)

        if (user==None):
            return JsonResponse({
                "error": "Credenciales inválidas"
            }, status=401)

        login(request, user)

        return JsonResponse({
            "mensaje": "Login exitoso",
            "token": tokens.get('id_token'),
            "nuevo_usuario": True
        })
    else:
        print("SALIÓ MAL EL REQUEST")
        return JsonResponse({
            "error": "Credenciales inválidas",
            "detalles": response.text
        }, status=401)
    
def cerrar_sesion(request):
    logout(request)
    
def get_or_create_usuario(username):
    try:
        usuario = Usuario.objects.get(login=username)
        
        print(f"Usuario encontrado: {usuario}")
        return usuario
    except Usuario.DoesNotExist:
        print(f"Usuario {username} no existe")
        usuario = None
        return None

def obtener_token_management_api():
    url = f"https://{os.getenv('AUTHZ_DOMAIN')}/oauth/token"
    payload = {
        "client_id": f"{os.getenv('CLIENT_ID')}",
        "client_secret": f"{os.getenv('CLIENT_SECRET')}",
        "audience": f"https://{os.getenv('AUTHZ_DOMAIN')}/api/v2/",
        "grant_type": "client_credentials"
    }
    headers = {"content-type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]


def crear_usuario_management_api(username, password):
    url = f"https://{os.getenv('AUTHZ_DOMAIN')}/api/v2/users"
    ACCESS_TOKEN = obtener_token_management_api()
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "connection": "Username-Password-Authentication",
        "username": username,
        "password": password,
        "user_metadata": {
            "username_original": username 
        }
    }
    response = requests.post(url, headers=headers, json=data)
    print("STATUS crear:", response.status_code)
    print("RESPONSE TEXT crear:", response.text)
    return response.json()






def verificar_token_auth0(token):
 
    try:
        
        
        jwks_url = f"https://{os.getenv('AUTHZ_DOMAIN')}/.well-known/jwks.json"
        jwks_client = jwt.PyJWKClient(jwks_url)
        

        signing_key = jwks_client.get_signing_key_from_jwt(token)
   
       
        
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=['RS256'],
            audience=[os.getenv('AUTHZ_AUDIENCE'),os.getenv('CLIENT_ID')],
            issuer=f"https://{os.getenv('AUTHZ_DOMAIN')}/"
        )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        return {'error': 'Token expirado'}
    except jwt.InvalidTokenError as e:
        return {'error': f'Token inválido: {str(e)}'}
    except Exception as e:
        return {'error': f'Error verificando token: {str(e)}'}

# def token_requerido(f):

#     @wraps(f)
#     def decorador(request, *args, **kwargs):
#         if hasattr(request, 'session') and 'access_token' in request.session:
#             token = request.session['id_token']
#         else:
#             auth_header = request.META.get('HTTP_AUTHORIZATION', '')
#             if auth_header.startswith('Bearer '):
#                 token = auth_header.split(' ')[1]
#             else:
#                 return JsonResponse({'error': 'Token requerido'}, status=401)
#         print(token)
#         print("ACÁ Se EsTa QUEDANDO")
#         resultado = verificar_token_auth0(token)
        
#         if 'error' in resultado:
#             return JsonResponse({'error': resultado['error']}, status=401)
#         print(resultado)
#         username = resultado.get('nickname')
#         username_original = resultado.get('user_metadata', {}).get('username_original')
#         print(username_original)
#         try:

#             usuario = Usuario.objects.get(login=username_original)
#             request.user = usuario
#         except Usuario.DoesNotExist:
#             return JsonResponse({'error': 'Usuario no encontrado en sistema'}, status=404)
        
#         return f(request, *args, **kwargs)
#     decorador.csrf_exempt = True
#     return decorador

def expedirTokenLogic(request):
    token = request.session.get('id_token')
    if not token:
        return JsonResponse({"error": "No hay token en la sesión"}, status=400)

    return JsonResponse({"token": token})
