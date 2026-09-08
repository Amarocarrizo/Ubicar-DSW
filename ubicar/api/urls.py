from rest_framework.routers import DefaultRouter
from ubicar.api.views import VehiculoViewsSet

router= DefaultRouter()
router.register('vehiculos',VehiculoViewsSet,basename='vehiculo')

urlpatterns=router.urls

