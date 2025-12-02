from django import forms
from .models import Usuario

from django.forms import ModelForm
from .models import Usuario

class UsuarioLoginForm(forms.Form):
    login = forms.CharField(label="Login", max_length=100)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
        
from Inventario.models import Bodega

class UsuarioCreateForm(forms.Form):
    nombre = forms.CharField(label="Nombre", max_length=100)
    apellido = forms.CharField(label="Apellido", max_length=100)
    login = forms.CharField(label="Login", max_length=100)
    contraseña = forms.CharField(label="Contraseña", max_length=100)
    rol = forms.ChoiceField(label="Rol", choices=[('JefeBodega', 'JefeBodega'), ('Operario', 'Operario'), ('Usuario', 'Usuario'), ('Vendedor', 'Vendedor')])
    bodegas = forms.ModelMultipleChoiceField(
        label="Bodegas", 
        queryset=Bodega.objects.all(), 
        widget=forms.SelectMultiple(attrs={'size': '6'}),
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        rol = cleaned_data.get('rol')
        bodegas = cleaned_data.get('bodegas')
        
        if rol in ['JefeBodega', 'Operario', 'Vendedor'] and not bodegas:
            self.add_error('bodegas', 'Debe seleccionar al menos una bodega.')
        elif rol == 'JefeBodega' and len(bodegas) > 1:
            self.add_error('bodegas', 'El Jefe de Bodega solo puede tener una bodega asignada.')
        return cleaned_data