#view se encarga del CRUD del modelo ubicar vehiculo
from rest_framework import viewsets
from ubicar.models import Vehiculo
from ubicar.models import Administrador
from ubicar.models import Conductor
from ubicar.models import Ruta
from ubicar.models import Posicion

from ubicar.api.serializer import VehiculoSerializer
from ubicar.api.serializer import AdministradorSerializer
from ubicar.api.serializer import ConductorSerializer
from ubicar.api.serializer import RutaSerializer
class VehiculoViewsSet(viewsets.ModelViewSet):
    queryset= Vehiculo.objects.all()
    serializer_class=VehiculoSerializer

class AdministradorViewsSet(viewsets.ModelViewSet):
    queryset=Administrador.objects.all()
    serializer_class=AdministradorSerializer

class ConductorViewsSet(viewsets.ModelViewSet):
    queryset= Conductor.objects.all()
    serializer_class= ConductorSerializer

class RutaViewsSet(viewsets.ModelViewSet):
    queryset= Ruta.objects.all()
    serializer_class= RutaSerializer

class PosicionViewsSet(viewsets.ModelViewSet):
    queryset= Posicion.objects.all()
    serializer_class= PosicionSerializer