from Pedido.models import Bodega
from Users.models import JefeBodega, Operario

def get_bodega_usuario(usuario, bodega_seleccionada_id=None):
    """
    Obtiene la bodega asociada al usuario autenticado.
    Para JefeBodega: retorna su bodega asignada
    Para Operario: retorna la bodega seleccionada o None si no ha seleccionado
    """
    if hasattr(usuario, 'jefebodega'):
        return usuario.jefebodega.bodega
    elif hasattr(usuario, 'operario'):
        if bodega_seleccionada_id:
            # Verificar que la bodega seleccionada esté en las bodegas del operario
            bodegas_operario = usuario.operario.bodega.all()
            try:
                bodega = bodegas_operario.get(id=bodega_seleccionada_id)
                return bodega
            except Bodega.DoesNotExist:
                return None
        return None  # Operario debe seleccionar una  bodega
    return None

def get_bodegas_operario(usuario):
    """
    Obtiene todas las bodegas asignadas a un operario
    """
    if hasattr(usuario, 'operario'):
        return usuario.operario.bodega.all()
    return []
