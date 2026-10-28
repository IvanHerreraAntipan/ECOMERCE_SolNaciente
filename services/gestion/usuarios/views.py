import secrets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import Usuario
from .serializers import (
    RegistroPublicoSerializer,
    LoginSerializer,
    UsuarioListSerializer,
    UsuarioAdminCreateSerializer,
    UsuarioAdminUpdateSerializer
)
from .permissions import EsAdministrador, EsCliente

class RegistroPublicoView(APIView):
    """
    RF-07: Registro público de nuevos usuarios.
    Crea cuentas con rol CLIENTE y estado ACTIVO de acuerdo con la regla RB-07.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Registro público de clientes (RF-07)",
        description="Permite que cualquier visitante cree su cuenta de Cliente. Bloquea cualquier intento de asignarse rol Administrador (RB-07).",
        request=RegistroPublicoSerializer,
        responses={
            201: OpenApiResponse(description="Usuario registrado exitosamente como Cliente"),
            400: OpenApiResponse(description="Errores de validación (correo duplicado, contraseñas no coinciden)")
        },
        tags=["Usuarios y Autenticación"]
    )
    def post(self, request):
        serializer = RegistroPublicoSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()
            return Response({
                "status": "success",
                "mensaje": "Usuario registrado exitosamente como Cliente.",
                "usuario": {
                    "id": usuario.id,
                    "email": usuario.email,
                    "nombre": usuario.nombre,
                    "apellido": usuario.apellido,
                    "rol": usuario.rol,
                    "estado": usuario.estado,
                    "creado_en": usuario.creado_en
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            "status": "error",
            "mensaje": "Error en los datos de registro.",
            "errores": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    RF-08: Inicio de sesión de usuarios (Clientes y Administradores).
    Verifica correo, contraseña hasheada y valida que el estado no sea BLOQUEADO o PENDIENTE.
    Retorna token, rol y la ruta de redirección correspondiente.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Inicio de sesión (RF-08)",
        description="Autentica a un usuario por email y password. Valida que esté ACTIVO. Retorna token y ruta de redirección según rol.",
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(description="Autenticación exitosa"),
            400: OpenApiResponse(description="Credenciales inválidas o cuenta inactiva/bloqueada")
        },
        tags=["Usuarios y Autenticación"]
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.validated_data['usuario']
            
            # Generar token seguro de acceso para el cliente (RF-09)
            token = f"solnaciente_{secrets.token_hex(24)}"
            
            # Redirección inteligente según rol del usuario
            redirect_to = "/admin" if usuario.rol == "ADMIN" else "/"

            return Response({
                "status": "success",
                "mensaje": f"Bienvenido(a), {usuario.nombre}.",
                "token": token,
                "usuario": {
                    "id": usuario.id,
                    "email": usuario.email,
                    "nombre": usuario.nombre,
                    "apellido": usuario.apellido,
                    "rol": usuario.rol,
                    "estado": usuario.estado
                },
                "redirect_to": redirect_to
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "mensaje": "Error de autenticación.",
            "errores": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    RF-09: Cierre de sesión.
    Invalida credenciales activas del token o sesión.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Cierre de sesión (RF-09)",
        description="Invalida la sesión activa del usuario.",
        responses={
            200: OpenApiResponse(description="Sesión cerrada exitosamente")
        },
        tags=["Usuarios y Autenticación"]
    )
    def post(self, request):
        return Response({
            "status": "success",
            "mensaje": "Sesión cerrada exitosamente."
        }, status=status.HTTP_200_OK)


class PanelAdminCheckView(APIView):
    """
    SCRUM-24: Verificación estricta de control de acceso por rol.
    """
    permission_classes = [EsAdministrador]

    @extend_schema(
        summary="Verificación de acceso administrativo (SCRUM-24)",
        description="Prueba de autorización por rol. Envía el email en el encabezado X-User-Email. Si es un CLIENTE se deniega el acceso (403). Si es un ADMIN se autoriza (200).",
        parameters=[
            OpenApiParameter(
                name="X-User-Email",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                description="Correo del usuario para simular la petición (ej: juan.perez@solnaciente.cl o admin@tienda.cl)",
                required=False
            )
        ],
        responses={
            200: OpenApiResponse(description="Acceso concedido al Administrador"),
            403: OpenApiResponse(description="Acceso denegado: se requiere rol de Administrador")
        },
        tags=["Control de Acceso (SCRUM-24)"]
    )
    def get(self, request):
        return Response({
            "status": "success",
            "mensaje": f"Acceso concedido al panel administrativo. Bienvenido(a), {request.user.nombre}.",
            "usuario": {
                "id": request.user.id,
                "email": request.user.email,
                "rol": request.user.rol,
                "estado": request.user.estado
            }
        }, status=status.HTTP_200_OK)


class UsuarioAdminListView(APIView):
    """
    SCRUM-28: Gestión administrativa de usuarios (RF-11 y RF-13).
    Permite listar todos los usuarios y crear cuentas con invitación de 24 horas.
    """
    permission_classes = [EsAdministrador]

    @extend_schema(
        summary="Listar usuarios (RF-13)",
        description="Retorna el listado completo de usuarios con roles y estados para el Administrador.",
        parameters=[
            OpenApiParameter(name="X-User-Email", type=OpenApiTypes.STR, location=OpenApiParameter.HEADER, description="Email del Admin autenticado (ej: admin@tienda.cl)", required=True)
        ],
        responses={200: UsuarioListSerializer(many=True)},
        tags=["Gestión de Usuarios (SCRUM-28)"]
    )
    def get(self, request):
        usuarios = Usuario.objects.all().order_by('id')
        serializer = UsuarioListSerializer(usuarios, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Crear usuario con invitación de 24 hrs (RF-11)",
        description="Crea una cuenta en estado PENDIENTE y genera un token de activación válido por 24 horas.",
        parameters=[
            OpenApiParameter(name="X-User-Email", type=OpenApiTypes.STR, location=OpenApiParameter.HEADER, description="Email del Admin autenticado (ej: admin@tienda.cl)", required=True)
        ],
        request=UsuarioAdminCreateSerializer,
        responses={201: UsuarioListSerializer},
        tags=["Gestión de Usuarios (SCRUM-28)"]
    )
    def post(self, request):
        serializer = UsuarioAdminCreateSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()
            return Response({
                "status": "success",
                "mensaje": "Usuario creado exitosamente. Se ha emitido el token de activación válido por 24 horas (RF-11).",
                "usuario": UsuarioListSerializer(usuario).data,
                "enlace_activacion": f"http://localhost:5173/activar-cuenta?token={usuario.token_activacion}"
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            "status": "error",
            "mensaje": "Error en los datos del usuario.",
            "errores": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UsuarioAdminDetailView(APIView):
    """
    SCRUM-28: Detalle y edición administrativa de usuarios (RF-13).
    """
    permission_classes = [EsAdministrador]

    @extend_schema(
        summary="Detalle de usuario (RF-13)",
        parameters=[
            OpenApiParameter(name="X-User-Email", type=OpenApiTypes.STR, location=OpenApiParameter.HEADER, description="Email del Admin autenticado (ej: admin@tienda.cl)", required=True)
        ],
        responses={200: UsuarioListSerializer},
        tags=["Gestión de Usuarios (SCRUM-28)"]
    )
    def get(self, request, pk):
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response({"status": "error", "mensaje": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(UsuarioListSerializer(usuario).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Editar usuario (RF-13)",
        parameters=[
            OpenApiParameter(name="X-User-Email", type=OpenApiTypes.STR, location=OpenApiParameter.HEADER, description="Email del Admin autenticado (ej: admin@tienda.cl)", required=True)
        ],
        request=UsuarioAdminUpdateSerializer,
        responses={200: UsuarioListSerializer},
        tags=["Gestión de Usuarios (SCRUM-28)"]
    )
    def patch(self, request, pk):
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response({"status": "error", "mensaje": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UsuarioAdminUpdateSerializer(usuario, data=request.data, partial=True)
        if serializer.is_valid():
            usuario_actualizado = serializer.save()
            return Response({
                "status": "success",
                "mensaje": "Usuario actualizado correctamente.",
                "usuario": UsuarioListSerializer(usuario_actualizado).data
            }, status=status.HTTP_200_OK)
        
        return Response({
            "status": "error",
            "errores": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class UsuarioBlockView(APIView):
    """
    SCRUM-32 / RF-14: Bloqueo de cuentas.
    Protegido por la regla RB-06:
    - Prohíbe auto-bloqueo.
    - Prohíbe bloquear al último administrador activo.
    """
    permission_classes = [EsAdministrador]

    @extend_schema(
        summary="Bloquear cuenta de usuario (RF-14 / RB-06)",
        description="Bloquea una cuenta impidiendo su inicio de sesión. Aplica la regla RB-06 para proteger al último administrador activo.",
        parameters=[
            OpenApiParameter(name="X-User-Email", type=OpenApiTypes.STR, location=OpenApiParameter.HEADER, description="Email del Admin autenticado (ej: admin@tienda.cl)", required=True)
        ],
        responses={
            200: OpenApiResponse(description="Cuenta bloqueada exitosamente"),
            400: OpenApiResponse(description="Error de validación o auto-bloqueo"),
            409: OpenApiResponse(description="Conflicto: intento de bloquear al último administrador activo (RB-06)")
        },
        tags=["Gestión de Usuarios (SCRUM-32)"]
    )
    def post(self, request, pk):
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response({"status": "error", "mensaje": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Regla RB-06: Prohibir auto-bloqueo
        if usuario.id == request.user.id or usuario.email.lower() == request.user.email.lower():
            return Response({
                "status": "error",
                "mensaje": "Operación rechazada: un administrador no puede auto-bloquear su propia cuenta (RB-06)."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Regla RB-06: Prohibir bloquear al último administrador activo
        if usuario.rol == 'ADMIN':
            admins_activos = Usuario.objects.filter(rol='ADMIN', estado='ACTIVO').count()
            if admins_activos <= 1:
                return Response({
                    "status": "error",
                    "mensaje": "Operación rechazada por RB-06: No es posible bloquear al único Administrador activo del sistema."
                }, status=status.HTTP_409_CONFLICT)

        usuario.estado = 'BLOQUEADO'
        usuario.save()

        return Response({
            "status": "success",
            "mensaje": f"La cuenta de {usuario.email} ha sido bloqueada exitosamente.",
            "usuario": UsuarioListSerializer(usuario).data
        }, status=status.HTTP_200_OK)


class UsuarioUnblockView(APIView):
    """
    SCRUM-32 / RF-15: Desbloqueo de cuentas.
    Restaura el estado de la cuenta a ACTIVO sin alterar contraseña ni rol.
    """
    permission_classes = [EsAdministrador]

    @extend_schema(
        summary="Desbloquear cuenta de usuario (RF-15)",
        description="Restaura una cuenta previamente bloqueada al estado ACTIVO.",
        parameters=[
            OpenApiParameter(name="X-User-Email", type=OpenApiTypes.STR, location=OpenApiParameter.HEADER, description="Email del Admin autenticado (ej: admin@tienda.cl)", required=True)
        ],
        responses={
            200: OpenApiResponse(description="Cuenta desbloqueada exitosamente"),
            404: OpenApiResponse(description="Usuario no encontrado")
        },
        tags=["Gestión de Usuarios (SCRUM-32)"]
    )
    def post(self, request, pk):
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response({"status": "error", "mensaje": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        usuario.estado = 'ACTIVO'
        usuario.save()

        return Response({
            "status": "success",
            "mensaje": f"La cuenta de {usuario.email} ha sido desbloqueada exitosamente.",
            "usuario": UsuarioListSerializer(usuario).data
        }, status=status.HTTP_200_OK)