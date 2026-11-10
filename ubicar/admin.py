"""
Admin de Django: es el ABM (alta, baja y modificación) de todas las entidades.
Acá solo se configura qué columnas, filtros y buscadores muestra cada tabla.
"""
from django.contrib import admin
from django.utils.html import format_html
from ubicar.models import (
    Administrador, Conductor, Vehiculo, AsignacionVehiculo, Ruta, Viaje,
    Posicion, Gasto, Alerta, estadoGasto, tipoDeGasto,
)

admin.site.site_header = 'UBICAR · Administración'
admin.site.site_title = 'UBICAR'
admin.site.index_title = 'Alta, baja y modificación de datos'


@admin.register(Conductor)
class ConductorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'dni', 'tipo_licencia', 'telefono', 'usuario')
    search_fields = ('nombre', 'apellido', 'dni')


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('patente', 'modelo', 'tipo_de_vehiculo', 'kilometraje', 'estado')
    list_filter = ('tipo_de_vehiculo', 'estado')
    search_fields = ('patente', 'modelo')


@admin.register(AsignacionVehiculo)
class AsignacionVehiculoAdmin(admin.ModelAdmin):
    list_display = ('conductor', 'vehiculo', 'fecha_desde', 'fecha_hasta', 'activa')
    list_filter = ('activa',)


@admin.register(Viaje)
class ViajeAdmin(admin.ModelAdmin):
    list_display = ('id_viaje', 'id_conductor', 'id_patente', 'id_ruta', 'estado', 'hora_inicio', 'hora_llegada')
    list_filter = ('estado',)


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ('id_gasto', 'viaje', 'tipo', 'descripcion', 'monto', 'km_registrado', 'estado', 'ver_comprobante', 'fecha_hora')
    list_filter = ('estado', 'tipo')
    readonly_fields = ('ver_comprobante_detalle',)

    def ver_comprobante(self, obj):
        if obj.comprobante:
            return format_html('<a href="{}" target="_blank">📄 Ver comprobante</a>', obj.comprobante.url)
        return "Sin archivo"
    ver_comprobante.short_description = 'Comprobante'

    def ver_comprobante_detalle(self, obj):
        if obj.comprobante:
            return format_html(
                '<a href="{0}" target="_blank">'
                '<img src="{0}" style="max-height: 250px; max-width: 400px; display: block; margin-bottom: 8px; border-radius: 4px; border: 1px solid #ccc;" onerror="this.style.display=\'none\'"/>'
                '📄 Abrir comprobante en pestaña nueva</a>',
                obj.comprobante.url
            )
        return "Sin archivo"
    ver_comprobante_detalle.short_description = 'Vista previa del comprobante'


@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ('id_alerta', 'viaje', 'tipo', 'estado', 'fecha_hora', 'fecha_revision', 'administrador')
    list_filter = ('tipo', 'estado')


@admin.register(Ruta)
class RutaAdmin(admin.ModelAdmin):
    list_display = ('id_ruta', 'origen', 'destino', 'distancia_estimada', 'tiempo_estimado')


@admin.register(Posicion)
class PosicionAdmin(admin.ModelAdmin):
    list_display = ('id_viaje', 'posicion_x', 'posicion_y', 'hora')


admin.site.register(Administrador)
admin.site.register(estadoGasto)
admin.site.register(tipoDeGasto)
