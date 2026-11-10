#archivo que permite establecer los permisos y restricciones de los usuarios (conductor y administrador) dentro de UBICAR
from rest_framework.permissions import BasePermission


class EsConductor(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, 'conductor')
        )


class EsAdministrador(BasePermission):

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.is_staff or request.user.is_superuser:
            return True
        try:
            return hasattr(request.user, 'administrador') and bool(request.user.administrador)
        except Exception:
            from ubicar.models import Administrador
            return Administrador.objects.filter(usuario=request.user).exists()