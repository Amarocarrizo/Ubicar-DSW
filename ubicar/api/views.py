#view se encarga del CRUD del modelo ubicar vehiculo
from rest_framework import viewsets
from ubicar.models import Vehiculo
from ubicar.models import Administrador
from ubicar.models import Conductor
from ubicar.models import Ruta
from ubicar.models import Posicion
from ubicar.models import Viaje
from ubicar.models import Gasto


from ubicar.api.serializer import VehiculoSerializer
from ubicar.api.serializer import AdministradorSerializer
from ubicar.api.serializer import ConductorSerializer
from ubicar.api.serializer import RutaSerializer
from ubicar.api.serializer import ViajeSerializer
from ubicar.api.serializer import PosicionSerializer
from ubicar.api.serializer import GastoSerializer

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

class ViajeViewsSet(viewsets.ModelViewSet):
    queryset= Viaje.objects.all()
    serializer_class= ViajeSerializer    

class PosicionViewsSet(viewsets.ModelViewSet):
    queryset= Posicion.objects.all()
    serializer_class= PosicionSerializer

class GastoViewsSet(viewsets.ModelViewSet):
    queryset= Gasto.objects.all()
    serializer_class= GastoSerializer