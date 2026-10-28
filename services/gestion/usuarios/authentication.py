from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Usuario

class SimpleTokenAuthentication(BaseAuthentication):
    """
    Autentica al usuario mediante el encabezado Authorization o X-User-Email.
    Permite validar roles y proteger rutas en Swagger y entre microservicios.
    """
    def authenticate(self, request):
        # 1. Probar con encabezado X-User-Email
        email = request.headers.get('X-User-Email')
        
        # 2. Si no viene, probar con Authorization: Bearer <email_o_token>
        if not email:
            auth_header = request.headers.get('Authorization')
            if auth_header:
                parts = auth_header.split()
                if len(parts) == 2 and parts[0].lower() in ['bearer', 'token']:
                    email = parts[1].strip()

        if not email:
            return None

        # Si el usuario envió email en el encabezado
        usuario = Usuario.objects.filter(email__iexact=email).first()
        if not usuario:
            return None

        if usuario.estado == 'BLOQUEADO':
            raise AuthenticationFailed("Esta cuenta ha sido bloqueada por la administración.")

        return (usuario, None)