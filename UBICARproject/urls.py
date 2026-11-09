"""
URL configuration for UBICARproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from ubicar import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/',include('ubicar.api.urls')),
    path('mapa/', views.ver_mapa),

    # Pantallas (front)
    path('', views.home),
    path('login/', views.login_view),
    path('conductor/', views.conductor_inicio),
    path('conductor/nuevo-viaje/', views.conductor_nuevo_viaje),
    path('conductor/viaje/<int:id_viaje>/', views.conductor_viaje),
    path('conductor/gasto/', views.conductor_gasto),
    path('conductor/viajes/', views.conductor_viajes),
    path('conductor/gastos/', views.conductor_gastos),
    path('conductor/perfil/', views.conductor_perfil),
    path(
        'api/login/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),

    path( #agrego validacion con token
        'api/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    )
    ]
