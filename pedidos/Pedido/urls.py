from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # URLs para vistas web tradicionales
    path('producto/crear', views.crear_producto, name='productoCreate'),
    path('bodegas/', views.bodega_list, name='bodegaList'),
    path('seleccionar-bodega/<int:bodega_id>/', views.seleccionar_bodega, name='seleccionarBodega'),
    path("", views.inventario_view, name="verInventario"),
    # URLs para API REST
    path('api/productos/crear/', api_views.crear_producto_api, name='api_crear_producto'),
    path('api/health-check/', api_views.health_check, name='api_health_check'),
    path('pedidos/crear', api_views.crear_pedido_api, name='api_crear_pedido'),
    path('pedidos/cambiar_estado', api_views.cambiar_estado_pedido_api, name='api_cambiar_estado_pedido'),
    path('pedidos/verificar_integridad', api_views.verificar_integridad, name='api_verificar_integridad'),
    path('pedidos/consultar/<int:id>/', api_views.consultar_pedido, name='api_consultar_pedido')
]
