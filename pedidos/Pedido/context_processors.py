from .logic.logic_bodega import get_bodegas_operario, get_bodega_usuario

def operario_context(request):
    """
    Context processor para hacer disponible información del operario en todos los templates
    """
    context = {
        'bodegas_operario': [],
        'bodega_actual': None,
        'es_operario': False
    }
    
    if request.user.is_authenticated and request.user.rol == 'Operario':
        context['es_operario'] = True
        context['bodegas_operario'] = get_bodegas_operario(request.user)
        
        # Obtener bodega seleccionada de la sesión
        bodega_seleccionada_id = request.session.get('bodega_seleccionada')
        if bodega_seleccionada_id:
            context['bodega_actual'] = get_bodega_usuario(request.user, bodega_seleccionada_id)
    elif request.user.is_authenticated and request.user.rol == 'JefeBodega':
        context['es_operario'] = False
        # Obtener bodega asignada al JefeBodega
        context['bodega_actual'] = get_bodega_usuario(request.user)
    return context