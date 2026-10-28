import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico es obligatorio')
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', 'ADMIN')
        extra_fields.setdefault('estado', 'ACTIVO')
        return self.create_user(email, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    ROLES = (('CLIENTE', 'Cliente'), ('ADMIN', 'Administrador'))
    ESTADOS = (('ACTIVO', 'Activo'), ('BLOQUEADO', 'Bloqueado'), ('PENDIENTE', 'Pendiente de activación'))

    email = models.EmailField(unique=True, db_index=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    rol = models.CharField(max_length=20, choices=ROLES, default='CLIENTE')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='ACTIVO')
    
    token_activacion = models.UUIDField(default=uuid.uuid4, null=True, blank=True)
    token_expira = models.DateTimeField(null=True, blank=True)
    
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    objects = UsuarioManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido']

    def __str__(self):
        return f"{self.email} ({self.rol})"

class ContenidoCMS(models.Model):
    SECCIONES = (('inicio_hero', 'Inicio Hero'), ('quienes_somos', 'Quiénes Somos'), ('contacto', 'Contacto'))
    seccion = models.CharField(max_length=50, primary_key=True, choices=SECCIONES)
    titulo = models.CharField(max_length=200)
    subtitulo = models.CharField(max_length=300, blank=True, null=True)
    cuerpo_texto = models.TextField(blank=True, null=True)
    banner_url = models.CharField(max_length=500, blank=True, null=True)
    boton_texto = models.CharField(max_length=50, blank=True, null=True)
    boton_enlace = models.CharField(max_length=200, blank=True, null=True)
    actualizado_en = models.DateTimeField(auto_now=True)

class ConfiguracionSitio(models.Model):
    TEMAS = (('dark-glass', 'Dark Glass'), ('sol-naciente', 'Sol Naciente'), 
             ('madera-carbono', 'Madera y Carbono'), ('pelota-blanca', 'Pelota 40+ Minimal'))
    clave = models.CharField(max_length=50, primary_key=True, default='tema_global')
    valor = models.CharField(max_length=50, choices=TEMAS, default='dark-glass')
    actualizado_en = models.DateTimeField(auto_now=True)

class MensajeContacto(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    mensaje = models.TextField()
    leido = models.BooleanField(default=False)
    fecha_recepcion = models.DateTimeField(auto_now_add=True)