from django.contrib import admin


from .models import Operario, Usuario, JefeBodega, Vendedor
# Register your models here.
admin.site.register(Usuario)
admin.site.register(Operario)
admin.site.register(JefeBodega)
admin.site.register(Vendedor)

