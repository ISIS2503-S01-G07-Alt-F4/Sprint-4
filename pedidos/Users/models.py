from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from Pedido.models import Bodega
# Código parcialmente tomado de: https://testdriven.io/blog/django-custom-user-model/

class UsuarioManager(BaseUserManager):
    def create_user(self, login, password=None, **extra_fields):
        if not login:
            raise ValueError('El usuario debe tener un login')
        user = self.model(login=login, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, login, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(login, password, **extra_fields)

# Create your models here.
class Usuario(AbstractBaseUser, PermissionsMixin):
    nombre = models.CharField(max_length=100, default="Sin nombre")
    apellido = models.CharField(max_length=100, blank=True)
    login = models.CharField(max_length=50, unique=True)
    rol = models.CharField(max_length=50, default="Usuario")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['nombre', 'apellido']

    objects = UsuarioManager()

    def __str__(self):
        return self.login

class Operario(Usuario):
    bodega = models.ManyToManyField('Pedido.Bodega')

class JefeBodega(Usuario):
    bodega = models.ForeignKey('Pedido.Bodega', on_delete=models.DO_NOTHING)

class Vendedor(Usuario):
    bodega = models.ManyToManyField('Pedido.Bodega')