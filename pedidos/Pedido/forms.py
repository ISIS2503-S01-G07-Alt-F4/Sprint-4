from django.forms import ModelForm
from .models import Producto, Estanteria

class ProductoForm(ModelForm):
    class Meta:
        model = Producto
        fields = ['codigo_barras', 'nombre', 'tipo', 'especificaciones', 'precio', 'estanteria']
    
    def __init__(self, *args, bodega=None, **kwargs):
        super().__init__(*args, **kwargs)
        if bodega:
            # Filtrar estanterías por la bodega del usuario
            self.fields['estanteria'].queryset = Estanteria.objects.filter(bodega=bodega)