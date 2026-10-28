from rest_framework import serializers
from .models import Usuario
import uuid
from datetime import timedelta
from django.utils import timezone

class RegistroPublicoSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text="Contraseña segura (mínimo 8 caracteres)"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Confirmación de la contraseña"
    )

    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'apellido', 'email', 'password', 'password_confirm']
        read_only_fields = ['id']

    def validate_email(self, value):
        """Valida que el correo sea único y esté normalizado en minúsculas."""
        email_normalizado = value.strip().lower()
        if Usuario.objects.filter(email__iexact=email_normalizado).exists():
            raise serializers.ValidationError("Ya existe una cuenta registrada con este correo electrónico.")
        return email_normalizado

    def validate(self, attrs):
        """Valida que ambas contraseñas coincidan."""
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                "password_confirm": "Las contraseñas ingresadas no coinciden."
            })
        return attrs

    def create(self, validated_data):
        """
        Crea el usuario asegurando la regla de negocio RB-07:
        El registro público asigna forzosamente el rol CLIENTE.
        """
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        usuario = Usuario(
            email=validated_data['email'],
            nombre=validated_data['nombre'].strip(),
            apellido=validated_data['apellido'].strip(),
            rol='CLIENTE',       # RB-07: Estrictamente forzado a CLIENTE
            estado='ACTIVO'      # Listo para operar de inmediato
        )
        usuario.set_password(password)  # Hash seguro PBKDF2 (RNF-12)
        usuario.save()
        return usuario

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        help_text="Correo electrónico registrado"
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="Contraseña del usuario"
    )

    def validate(self, attrs):
        email = attrs.get('email', '').strip().lower()
        password = attrs.get('password', '')

        try:
            usuario = Usuario.objects.get(email__iexact=email)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("Credenciales inválidas. Correo o contraseña incorrectos.")

        # Verificar contraseña con el hash seguro PBKDF2
        if not usuario.check_password(password):
            raise serializers.ValidationError("Credenciales inválidas. Correo o contraseña incorrectos.")

        # Regla RF-08 / RF-14: Verificar estado de la cuenta
        if usuario.estado == 'BLOQUEADO':
            raise serializers.ValidationError("Tu cuenta ha sido bloqueada por la administración de la tienda.")
        
        if usuario.estado == 'PENDIENTE':
            raise serializers.ValidationError("Tu cuenta se encuentra pendiente de activación.")

        attrs['usuario'] = usuario
        return attrs    

class UsuarioListSerializer(serializers.ModelSerializer):
    """Serializer para listar y ver detalles de usuarios en el panel administrativo."""
    class Meta:
        model = Usuario
        fields = ['id', 'email', 'nombre', 'apellido', 'rol', 'estado', 'token_activacion', 'token_expira', 'creado_en']


class UsuarioAdminCreateSerializer(serializers.ModelSerializer):
    """
    RF-11: Creación administrativa de cuentas.
    Genera cuenta en estado PENDIENTE con token de activación de 24 horas.
    """
    rol = serializers.ChoiceField(choices=['CLIENTE', 'ADMIN'], default='CLIENTE')

    class Meta:
        model = Usuario
        fields = ['id', 'email', 'nombre', 'apellido', 'rol']
        read_only_fields = ['id']

    def validate_email(self, value):
        email_normalizado = value.strip().lower()
        if Usuario.objects.filter(email__iexact=email_normalizado).exists():
            raise serializers.ValidationError("Ya existe un usuario con este correo electrónico.")
        return email_normalizado

    def create(self, validated_data):
        # Generar token de activación de 24 horas (RF-11)
        token_activacion = uuid.uuid4()
        token_expira = timezone.now() + timedelta(hours=24)

        usuario = Usuario(
            email=validated_data['email'].strip().lower(),
            nombre=validated_data['nombre'].strip(),
            apellido=validated_data['apellido'].strip(),
            rol=validated_data.get('rol', 'CLIENTE'),
            estado='PENDIENTE',  # Inicia pendiente hasta activar
            token_activacion=token_activacion,
            token_expira=token_expira
        )
        # Contraseña provisional aleatoria e inusable hasta activación
        usuario.set_password(uuid.uuid4().hex)
        usuario.save()
        return usuario


class UsuarioAdminUpdateSerializer(serializers.ModelSerializer):
    """RF-13: Edición administrativa de usuarios."""
    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'email', 'rol']