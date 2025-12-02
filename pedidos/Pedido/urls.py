from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.crear_pedido_api, name='crear_pedido'),
    path('<int:id>/', api_views.consultar_pedido, name='consultar_pedido'),
    path('<int:id>/estado', api_views.cambiar_estado_pedido_api, name='cambiar_estado_pedido'),
    path('<int:id>/integridad', api_views.verificar_integridad, name='verificar_integridad'),
]
