from rest_framework.routers import DefaultRouter
from ubicar.api.views import VehiculoViewsSet
from ubicar.api.views import AdministradorViewsSet
from ubicar.api.views import ConductorViewsSet

router= DefaultRouter()
router.register('vehiculos',VehiculoViewsSet,basename='vehiculo')
router.register('administrador',AdministradorViewsSet,basename='administrador')
router.register('conductores',ConductorViewsSet,basename='conductor')
urlpatterns=router.urls

