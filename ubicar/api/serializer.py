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
from ubicar.models import tipoDeGasto

class TipoDeGastoSerializer(serializers.ModelSerializer):
    class Meta:
        model = tipoDeGasto
        fields = '__all__'

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
    # Además de los ids, se devuelven los datos de la ruta, el vehículo y el conductor
    # (solo lectura) para que el front no tenga que hacer un pedido extra por cada viaje.
    ruta = RutaSerializer(source='id_ruta', read_only=True)
    vehiculo = VehiculoSerializer(source='id_patente', read_only=True)
    conductor = ConductorSerializer(source='id_conductor', read_only=True)

    class Meta:
        model= Viaje
        fields= '__all__'
        read_only_fields = [
            'id_conductor',
            'hora_inicio'
        ]

class GastoSerializer(serializers.ModelSerializer):
    estado_nombre = serializers.CharField(
            source='estado.estado',
            read_only=True
            )
    class Meta:
        model = Gasto
        fields = '__all__'
        read_only_fields = [
            'viaje',
            'estado',
            'fecha_hora'
        ] #solo lectura, asi el conductor no puede elegir manualmente viaje ni gasto
class AlertaSerializer(serializers.ModelSerializer):
    class Meta:
        model= Alerta
        fields= '__all__'