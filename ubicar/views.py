from django.shortcuts import render

def ver_mapa(request):
    return render(request, 'index.html')
