from rest_framework import serializers

from ubicar.models import Vehiculo

class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model= Vehiculo
        fields= '__all__'