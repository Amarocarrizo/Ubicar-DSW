from django.contrib import admin
from ubicar.models import (
    Administrador,
    Conductor,Licencia,TipoDeVehiculo,EstadoViaje,estadoGasto,tipoDeGasto,AlertaDefinida,
    AsignacionVehiculo,
    Vehiculo,
    Ruta,
    Viaje,
    Posicion,
    Gasto
)

# Register your models here.

admin.site.register(Administrador)
admin.site.register(Conductor)
admin.site.register(AsignacionVehiculo)
admin.site.register(Vehiculo)
admin.site.register(Ruta)
admin.site.register(Viaje)
admin.site.register(Posicion)
admin.site.register(Gasto)
admin.site.register(Licencia)
admin.site.register(TipoDeVehiculo)
admin.site.register(EstadoViaje)
admin.site.register(estadoGasto)
admin.site.register(tipoDeGasto)
admin.site.register(AlertaDefinida)
