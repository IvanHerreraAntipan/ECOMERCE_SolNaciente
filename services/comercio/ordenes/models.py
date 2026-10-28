import uuid
from django.db import models

class Carrito(models.Model):
    usuario_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    session_key = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, related_name='items', on_delete=models.CASCADE)
    producto_id = models.CharField(max_length=64)
    cantidad = models.PositiveIntegerField(default=1)

class Orden(models.Model):
    ESTADOS = (
        ('PENDIENTE_PAGO', 'Pendiente de Pago'),
        ('CONFIRMACION_PENDIENTE', 'Confirmación Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('RECHAZADA', 'Rechazada'),
        ('CANCELADA', 'Cancelada'),
        ('VENCIDA', 'Vencida'),
        ('REVISION_REQUERIDA', 'Revisión Requerida'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cliente_id = models.BigIntegerField(db_index=True)
    estado = models.CharField(max_length=30, choices=ESTADOS, default='PENDIENTE_PAGO')
    moneda = models.CharField(max_length=3, default='CLP')
    subtotal = models.BigIntegerField()
    total = models.BigIntegerField()
    reserva_id = models.CharField(max_length=64, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)

class ItemOrden(models.Model):
    orden = models.ForeignKey(Orden, related_name='items', on_delete=models.CASCADE)
    producto_id = models.CharField(max_length=64)
    nombre_historico = models.CharField(max_length=200)
    precio_unitario_historico = models.BigIntegerField()
    cantidad = models.PositiveIntegerField()
    subtotal_linea = models.BigIntegerField()

class TransaccionPago(models.Model):
    orden = models.OneToOneField(Orden, on_delete=models.CASCADE, related_name='pago')
    token_ws = models.CharField(max_length=100, unique=True)
    codigo_autorizacion = models.CharField(max_length=50, null=True, blank=True)
    monto = models.BigIntegerField()
    estado = models.CharField(max_length=20, default='INICIADA')
    fecha_transaccion = models.DateTimeField(auto_now_add=True)