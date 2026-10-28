"""
URL configuration for config project (Servicio de Catálogo e Inventario).
"""
from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from .mongo import get_db

@api_view(['GET'])
def health_check(request):
    """Verifica la conexión viva con MongoDB y el Replica Set."""
    try:
        db = get_db()
        db.command('ping')
        return Response({
            'status': 'ok',
            'servicio': 'catalogo-inventario',
            'mongodb': 'conectado con éxito',
            'database': db.name
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'mongodb': 'error de conexión',
            'detalle': str(e)
        }, status=500)

urlpatterns = [
    # Endpoint de verificación de salud
    path('api/health/', health_check, name='health-check'),
    
    # Documentación OpenAPI (RNF-05)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]