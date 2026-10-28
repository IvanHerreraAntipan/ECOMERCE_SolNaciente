import uuid
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers

# Credenciales oficiales de Transbank Webpay Plus (Ambiente de Integración / Sandbox)
TBK_COMMERCE_CODE = "597055555532"
TBK_API_KEY = "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C"
TBK_BASE_URL = "https://webpay3gint.transbank.cl"
TBK_RETURN_URL = "http://localhost:5173/pago-resultado"

@extend_schema(
    summary="Iniciar pago en Sandbox (Transbank Webpay Plus)",
    description="Crea una transacción de prueba en Transbank y devuelve el token_ws y la URL del formulario de pago.",
    request=inline_serializer(
        name="IniciarPagoRequest",
        fields={
            "monto": serializers.IntegerField(default=25990, help_text="Monto en CLP"),
            "orden_id": serializers.CharField(required=False, default="SOL-1001", help_text="Identificador de la orden")
        }
    )
)
@api_view(['POST'])
def iniciar_pago_sandbox(request):
    """Crea una transacción oficial de prueba en Webpay Plus Integración."""
    monto = int(request.data.get('monto') or request.data.get('amount') or 25990)
    orden_id = str(request.data.get('orden_id') or request.data.get('buy_order') or f"SOL-{uuid.uuid4().hex[:6].upper()}")
    session_id = str(request.data.get('session_id') or f"SES-{uuid.uuid4().hex[:6].upper()}")
    return_url = request.data.get('return_url') or TBK_RETURN_URL

    headers = {
        'Tbk-Api-Key-Id': TBK_COMMERCE_CODE,
        'Tbk-Api-Key-Secret': TBK_API_KEY,
        'Content-Type': 'application/json'
    }

    payload = {
        "buy_order": orden_id,
        "session_id": session_id,
        "amount": monto,
        "return_url": return_url
    }

    try:
        endpoint = f"{TBK_BASE_URL}/rswebpaytransaction/api/webpay/v1.2/transactions"
        response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return Response({
                "status": "success",
                "mensaje": "Transacción creada exitosamente en Transbank Webpay Plus Sandbox",
                "pasarela": "Transbank Webpay Plus (Integración)",
                "orden_id": orden_id,
                "monto_clp": monto,
                "token_ws": data.get("token"),
                "url_webpay": data.get("url")
            })
        else:
            return Response({
                "status": "error",
                "mensaje": "Transbank rechazó la creación de la transacción",
                "detalle": response.text
            }, status=response.status_code)

    except Exception as e:
        return Response({
            "status": "error",
            "mensaje": "Error de comunicación con Transbank",
            "error": str(e)
        }, status=500)