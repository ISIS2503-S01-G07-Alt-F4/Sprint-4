from django.http import JsonResponse
from Users.logic.logic_usuario import token_requerido


def _deprecated_response():
    return JsonResponse({
        'detail': 'Esta vista ha sido reemplazada por los endpoints de la API de pedidos.'
    }, status=410)


@token_requerido
def inventario_view(request):
    return _deprecated_response()


@token_requerido
def bodega_list(request):
    return _deprecated_response()


@token_requerido
def crear_producto(request):
    return _deprecated_response()


@token_requerido
def seleccionar_bodega(request, bodega_id):
    return _deprecated_response()