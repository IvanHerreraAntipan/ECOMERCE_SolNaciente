"""
URL configuration for config project (Servicio de Comercio).
"""
from django.contrib import admin
from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from ordenes.views import iniciar_pago_sandbox

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Endpoint de Pasarela Sandbox (SCRUM-22 / RF-31)
    path('api/payments/init/', iniciar_pago_sandbox, name='iniciar-pago'),

    # Documentación OpenAPI (RNF-05)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]