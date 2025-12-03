from django import forms

class UsuarioLoginForm(forms.Form):
    login = forms.CharField(label="Login", max_length=100)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
        
class UsuarioCreateForm(forms.Form):
    nombre = forms.CharField(label="Nombre", max_length=100)
    apellido = forms.CharField(label="Apellido", max_length=100)
    login = forms.CharField(label="Login", max_length=100)
    contraseña = forms.CharField(label="Contraseña", max_length=100)
    rol = forms.ChoiceField(label="Rol", choices=[('JefeBodega', 'JefeBodega'), ('Operario', 'Operario'), ('Usuario', 'Usuario'), ('Vendedor', 'Vendedor')])

    def clean(self):
        cleaned_data = super().clean()
        rol = cleaned_data.get('rol')
        return cleaned_data