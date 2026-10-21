#view se encarga del CRUD del modelo ubicar vehiculo
from rest_framework import viewsets, status
from ubicar.models import Vehiculo
from ubicar.models import Administrador
from ubicar.models import Conductor
from ubicar.models import Ruta
from ubicar.models import Posicion
from ubicar.models import Viaje
from ubicar.models import Gasto
from ubicar.models import Alerta
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from ubicar.api.serializer import VehiculoSerializer
from ubicar.api.serializer import AdministradorSerializer
from ubicar.api.serializer import ConductorSerializer
from ubicar.api.serializer import RutaSerializer
from ubicar.api.serializer import ViajeSerializer
from ubicar.api.serializer import PosicionSerializer
from ubicar.api.serializer import GastoSerializer
from ubicar.api.serializer import AlertaSerializer

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
    @action(detail=True, methods=['post'])
    def iniciar(self, request, pk=None):
        viaje = self.get_object()
        latitud = request.data.get('latitud')
        longitud = request.data.get('longitud')

        if latitud is None or longitud is None:
            return Response(
                {'error': 'Debe enviar latitud y longitud iniciales'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            viaje.iniciar_viaje(latitud, longitud)
            return Response({'mensaje': 'Viaje iniciado correctamente'})
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
class PosicionViewsSet(viewsets.ModelViewSet):
    queryset= Posicion.objects.all()
    serializer_class= PosicionSerializer

class GastoViewsSet(viewsets.ModelViewSet):
    queryset= Gasto.objects.all()
    serializer_class= GastoSerializer

class AlertaViewsSet(viewsets.ModelViewSet):
    queryset= Alerta.objects.all()
    serializer_class= AlertaSerializer

