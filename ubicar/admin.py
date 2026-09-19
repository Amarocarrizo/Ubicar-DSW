from django.contrib import admin
from ubicar.models import (
    Administrador,
    Conductor,
    Vehiculo,
    Ruta,
    Viaje,
    Posicion,
    Gasto
)

# Register your models here.

admin.site.register(Administrador)
admin.site.register(Conductor)
admin.site.register(Vehiculo)
admin.site.register(Ruta)
admin.site.register(Viaje)
admin.site.register(Posicion)
admin.site.register(Gasto)
