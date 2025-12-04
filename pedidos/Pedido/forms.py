from django import forms


class ProductoForm(forms.Form):
    codigo_barras = forms.CharField(max_length=100)
    nombre = forms.CharField(max_length=100)
    tipo = forms.CharField(max_length=50)
    especificaciones = forms.CharField(widget=forms.Textarea)
    precio = forms.DecimalField(max_digits=12, decimal_places=2)
    estanteria = forms.CharField(max_length=100, required=False)