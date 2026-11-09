from django.shortcuts import render, redirect

# Estas vistas solo entregan el HTML de cada pantalla.
# Los datos los pide el JavaScript de la pantalla a la API (/api/...) con el token JWT.


def home(request):
    return redirect('/login/')


def login_view(request):
    return render(request, 'login.html')


def ver_mapa(request):
    return render(request, 'index.html')
