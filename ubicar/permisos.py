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
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, 'administrador')
        )