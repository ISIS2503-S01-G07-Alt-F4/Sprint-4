from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse

from Users.forms import UsuarioCreateForm, UsuarioLoginForm
from Users.logic.logic_usuario import login_usuario, cerrar_sesion
from Users.models import Usuario, JefeBodega, Operario
from Users.logic.logic_usuario import create_usuario
# Create your views here.

import logging
logger = logging.getLogger(__name__)

def usuario_login(request):
    print("ESTO")
    if request.method == 'POST':
        form = UsuarioLoginForm(request.POST)
        #print(form)
        print(form.is_valid())
        if form.is_valid():
            print("ESTO1")
            logger.info("Va a comenzar el login")
            usuario = login_usuario(request, form)
            if usuario is not None:
                print("NOT NONE")
                messages.add_message(request, messages.SUCCESS, "Inicio de sesión exitoso")
            else:
                print("NONE")
                messages.add_message(request, messages.ERROR, "Credenciales inválidas")
        else:
            print(form.errors)
    else:
        form = UsuarioLoginForm()
    
    context = {
        'form': form
    }
    return render(request, 'Usuario/usuarioLogin.html', context)

def usuario_login_postman(request):
    print("ESTO")
    if request.method == 'POST':
        form = UsuarioLoginForm(request.POST)
        #print(form)
        print(form.is_valid())
        if form.is_valid():
            print("ESTO1")
            logger.info("Va a comenzar el login")
            usuario = login_usuario(request, form)
            if usuario is not None:
                print("NOT NONE")
                messages.add_message(request, messages.SUCCESS, "Inicio de sesión exitoso")
                return usuario
            else:
                print("NONE")
                messages.add_message(request, messages.ERROR, "Credenciales inválidas")
        else:
            print(form.errors)
    else:
        form = UsuarioLoginForm()
    
    context = {
        'form': form
    }
    return render(request, 'Usuario/usuarioLogin.html', context)

def usuario_logout(request):
    cerrar_sesion(request)
    return HttpResponseRedirect(reverse('usuarioLogin'))

def usuario_create(request):
    if request.method == 'POST':
        form = UsuarioCreateForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            create_usuario(data)
            return HttpResponseRedirect(reverse('usuarioCreate'))
        else:
            print(form.errors)
    else:
        form = UsuarioCreateForm()
    context = {'form': form}
    return render(request, 'Usuario/usuarioCreate.html', context)