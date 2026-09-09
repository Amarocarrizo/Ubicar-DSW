from rest_framework import serializers

from ubicar.models import Vehiculo
from ubicar.models import Administrador
from ubicar.models import Conductor

class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model= Vehiculo
        fields= '__all__'

class AdministradorSerializer(serializers.ModelSerializer):
    class Meta:
        model= Administrador
        fields= '__all__'

class ConductorSerializer(serializers.ModelSerializer):
    class Meta:
        model= Conductor
        fields= '__all__'