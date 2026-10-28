from rest_framework.permissions import BasePermission

class EsAdministrador(BasePermission):
    """
    Permite el acceso únicamente a usuarios con rol ADMIN o superusuarios activos.
    """
    message = "Acceso denegado: se requieren permisos de Administrador."

    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (getattr(request.user, 'rol', None) == 'ADMIN' or getattr(request.user, 'is_superuser', False)) and 
            getattr(request.user, 'estado', 'ACTIVO') == 'ACTIVO'
        )


class EsCliente(BasePermission):
    """
    Permite el acceso a usuarios autenticados con rol CLIENTE y estado ACTIVO.
    """
    message = "Acceso denegado: se requiere una cuenta de Cliente activa."

    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            getattr(request.user, 'rol', None) == 'CLIENTE' and 
            getattr(request.user, 'estado', None) == 'ACTIVO'
        )