from django.shortcuts import render, redirect

# Estas vistas solo entregan el HTML de cada pantalla.
# Los datos los pide el JavaScript de la pantalla a la API (/api/...) con el token JWT.


def home(request):
    return redirect('/login/')


def login_view(request):
    return render(request, 'login.html')


# --- Conductor (app móvil) ---
def conductor_inicio(request):
    return render(request, 'conductor/inicio.html')


def conductor_nuevo_viaje(request):
    return render(request, 'conductor/nuevo_viaje.html')


def conductor_viaje(request, id_viaje):
    return render(request, 'conductor/viaje.html', {'id_viaje': id_viaje})


def conductor_gasto(request):
    return render(request, 'conductor/gasto.html')


def conductor_viajes(request):
    return render(request, 'conductor/viajes.html')


def conductor_gastos(request):
    return render(request, 'conductor/gastos.html')


def conductor_perfil(request):
    return render(request, 'conductor/perfil.html')


def ver_mapa(request):
    return render(request, 'index.html')
