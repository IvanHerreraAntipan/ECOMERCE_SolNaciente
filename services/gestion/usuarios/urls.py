from django.urls import path
from .views import (
    RegistroPublicoView,
    LoginView,
    LogoutView,
    PanelAdminCheckView,
    UsuarioAdminListView,
    UsuarioAdminDetailView,
    UsuarioBlockView,
    UsuarioUnblockView
)

urlpatterns = [
    # Endpoints Públicos / Clientes
    path('registro/', RegistroPublicoView.as_view(), name='registro_publico'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('admin-check/', PanelAdminCheckView.as_view(), name='admin_check'),

    # Endpoints Administrativos (SCRUM-28)
    path('admin/usuarios/', UsuarioAdminListView.as_view(), name='admin_usuarios_list'),
    path('admin/usuarios/<int:pk>/', UsuarioAdminDetailView.as_view(), name='admin_usuarios_detail'),

    # Bloqueo y Desbloqueo (SCRUM-32)
    path('admin/usuarios/<int:pk>/block/', UsuarioBlockView.as_view(), name='admin_usuarios_block'),
    path('admin/usuarios/<int:pk>/unblock/', UsuarioUnblockView.as_view(), name='admin_usuarios_unblock'),
]