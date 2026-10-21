from rest_framework import serializers

from ubicar.models import Vehiculo
from ubicar.models import Administrador
from ubicar.models import Conductor
from ubicar.models import Ruta
from ubicar.models import Posicion
from ubicar.models import Viaje
from ubicar.models import Gasto
from ubicar.models import Alerta
from ubicar.models import AsignacionVehiculo

class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model= Vehiculo
        fields= '__all__'

class AdministradorSerializer(serializers.ModelSerializer):
    class Meta:
        model= Administrador
        fields= '__all__'

class AsignacionVehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsignacionVehiculo
        fields = '__all__'

class ConductorSerializer(serializers.ModelSerializer):
    class Meta:
        model= Conductor
        fields= '__all__'

class RutaSerializer(serializers.ModelSerializer):
    class Meta:
        model= Ruta
        fields= '__all__'

class PosicionSerializer(serializers.ModelSerializer):
    class Meta:
        model= Posicion
        fields= '__all__'


class ViajeSerializer(serializers.ModelSerializer):
    class Meta:
        model= Viaje
        fields= '__all__'

class GastoSerializer(serializers.ModelSerializer):
    class Meta:
        model= Gasto
        fields= '__all__'

class AlertaSerializer(serializers.ModelSerializer):
    class Meta:
        model= Alerta
        fields= '__all__'