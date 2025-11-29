from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from Pedido.forms import ProductoForm
from Pedido.logic.logic_inventario import get_bodegas
from Pedido.logic.logic_bodega import get_bodega_usuario, get_bodegas_operario
from Pedido.logic.logic_producto import registrar_producto, obtener_productos
from Users.logic.logic_usuario import token_requerido

@token_requerido
def inventario_view(request):
    # if request.user.is_authenticated:
    #     rol = request.user.rol
    # else:
    #     rol = None
    rol = request.user.rol
    productos = obtener_productos()
    return render(request, 'Inventario/Pedido.html',{
            'rol':rol,
            'productos': productos
    })

@token_requerido
def bodega_list(request):
    # if request.user.is_authenticated:
    #     rol = request.user.rol
    # else:
    #     rol = None
    # print(request.user)
    rol = request.user.rol
    bodegas = get_bodegas()
    return render(request, 'Bodega/bodega.html', {
        'bodegas': bodegas, 
        'rol': rol
    })

@token_requerido
def crear_producto(request):
    # if request.user.is_authenticated:
    #     rol = request.user.rol
    #     # Obtener bodega seleccionada de la sesión para operarios
    #     bodega_seleccionada_id = request.session.get('bodega_seleccionada')
    #     bodega_usuario = get_bodega_usuario(request.user, bodega_seleccionada_id)
    # else:
    #     rol = None
    #     bodega_usuario = None
    rol = request.user.rol
    #     # Obtener bodega seleccionada de la sesión para operarios
    bodega_seleccionada_id = request.session.get('bodega_seleccionada')
    bodega_usuario = get_bodega_usuario(request.user, bodega_seleccionada_id)
        
    # Verificar que el usuario tenga una bodega asignada
    if not bodega_usuario and request.user.is_authenticated:
        if rol == 'Operario':
            messages.error(request, "Debes seleccionar una bodega desde el menú superior.")
        else:
            messages.error(request, "No tienes una bodega asignada. Contacta al administrador.")
        return render(request, 'Producto/crearProducto.html', {
            'form': None, 
            'rol': rol
        })
        
    if request.method == 'POST':
        form = ProductoForm(request.POST, bodega=bodega_usuario)
        if form.is_valid():
            data = form.cleaned_data
            try:
                registrar_producto(data)
                messages.success(request, "Producto creado exitosamente")
                return HttpResponseRedirect(reverse('productoCreate'))
            except ValueError as e:
                messages.error(request, str(e))
        else:
            print(form.errors)
    else:
        form = ProductoForm(bodega=bodega_usuario)
    context = {
        'form': form, 
        'rol': rol
    }
    return render(request, 'Producto/crearProducto.html', context)


def seleccionar_bodega(request, bodega_id):
    """
    Vista para que los operarios seleccionen su bodega de trabajo
    """
    if request.user.is_authenticated and request.user.rol == 'Operario':
        # Verificar que la bodega pertenezca al operario
        bodegas_operario = get_bodegas_operario(request.user)
        if bodegas_operario.filter(id=bodega_id).exists():
            request.session['bodega_seleccionada'] = bodega_id
            messages.success(request, "Bodega seleccionada correctamente")
        else:
            messages.error(request, "No tienes acceso a esa bodega")
    else:
        messages.error(request, "No tienes permisos para realizar esta acción")
    
    # Redirigir a la página anterior o al inicio
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))