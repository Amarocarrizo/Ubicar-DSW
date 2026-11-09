from rest_framework.routers import DefaultRouter
from ubicar.api.views import VehiculoViewsSet
from ubicar.api.views import AdministradorViewsSet
from ubicar.api.views import ConductorViewsSet
from ubicar.api.views import RutaViewsSet
from ubicar.api.views import PosicionViewsSet
from ubicar.api.views import ViajeViewsSet
from ubicar.api.views import GastoViewsSet
from ubicar.api.views import AlertaViewsSet
from ubicar.api.views import AsignacionVehiculoViewSet
from ubicar.api.views import MeView, TipoDeGastoViewSet
from django.urls import path
router= DefaultRouter()
router.register('vehiculos',VehiculoViewsSet,basename='vehiculo')
router.register('administrador',AdministradorViewsSet,basename='administrador')
router.register('asignaciones', AsignacionVehiculoViewSet,basename= 'asignacionVehiculo')
router.register('conductores',ConductorViewsSet,basename='conductor')
router.register('ruta',RutaViewsSet,basename='ruta')
router.register('posicion',PosicionViewsSet,basename='posicion')
router.register('viaje',ViajeViewsSet,basename='viaje')
router.register('gasto',GastoViewsSet,basename='gasto')
router.register('alerta',AlertaViewsSet,basename='alerta')
router.register('tipos-gasto', TipoDeGastoViewSet, basename='tipoGasto')

urlpatterns = [path('me/', MeView.as_view(), name='me')] + router.urls

