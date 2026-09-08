#view se encarga del CRUD del modelo ubicar vehiculo
from rest_framework import viewsets
from ubicar.models import Vehiculo
from ubicar.api.serializer import VehiculoSerializer
class VehiculoViewsSet(viewsets.ModelViewSet):
    queryset= Vehiculo.objects.all()
    serializer_class=VehiculoSerializer
