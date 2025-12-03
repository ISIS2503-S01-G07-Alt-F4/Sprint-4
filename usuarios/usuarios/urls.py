from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('crearusuario/', csrf_exempt(views.usuario_create), name='usuarioCreate'),
    path('login/', csrf_exempt(views.usuario_login), name='usuarioLogin'),
    path('loginP/', csrf_exempt(views.usuario_login_postman), name='usuarioLoginPostman'),
    path('logout/', csrf_exempt(views.usuario_logout), name='usuarioLogout'),
    path('expedirToken/', csrf_exempt(views.expedirToken), name='expedicionToken'),
]
