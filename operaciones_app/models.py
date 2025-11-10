from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from mantenimiento_app.models import Vehiculo

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=10)
    direccion = models.TextField()

    def __str__(self):
        return f"Perfil de {self.user.username}"
    

class Localidades(models.Model):
    nombre_localidad = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre_localidad}"
    

class Ruta(models.Model):
    ubicacion = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.ubicacion}"
    

class Turno(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name}"
    

class EstadoRuta(models.Model):
    estado = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.estado}"


class SolicitudRuta(models.Model):
    fecha_solicitud = models.DateTimeField(default=timezone.now)
    operador = models.CharField(max_length=10)
    telefono = models.CharField(max_length=10)
    turno = models.ForeignKey(Turno, on_delete=models.CASCADE)
    fecha_recogida = models.DateTimeField()
    localidad = models.ForeignKey(Localidades, on_delete=models.CASCADE)
    barrio = models.CharField(max_length=50)
    ubicacion = models.URLField()
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=100)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    estado = models.ForeignKey(EstadoRuta, on_delete=models.CASCADE, default=1) 

    def __str__(self):
        return f"{self.operador}" + f"{self.fecha_solicitud}"
    

class CancelacionRuta(models.Model):
    fecha_cancelacion = models.DateTimeField()
    operador = models.CharField(max_length=10)
    descripcion = models.TextField()
    solicitud = models.ForeignKey(SolicitudRuta, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.operador}"
    

# Modelos checkeo de flota

class OrdenFlota(models.Model):
    fecha = models.DateField()
    numero_bus = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)

    def __str__(self):
        return f"Orden de flota {self.numero_bus} - {self.fecha}"
    

class RutaFlota(models.Model):
    ruta = models.CharField(max_length=20)
    
    def __str__(self):
        return f"Ruta de flota {self.ruta}"


class TurnoFlota(models.Model):
    TURNO_CHOICES = [
        ('1', 'Primer Turno'),
        ('2', 'Segundo Turno'),
        ('3', 'Tercer Turno'),
    ]
    turno = models.CharField(max_length=1, choices=TURNO_CHOICES)
    codigo_operador = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre_operador  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nombre_operador')
    apellido_operador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='apellido_operador')
    ruta = models.ForeignKey(RutaFlota, on_delete=models.CASCADE)
    tabla = models.CharField(max_length=50)
    INSTANTE = [
        ('IP', 'Inicio patio'),
        ('IO', 'Inicio Operacion'),
        ('FO', 'Fin Operacion'),
        ('EP', 'Entra Patio'),
    ]
    instante = models.CharField(max_length=2, choices=INSTANTE)
    km = models.DecimalField(max_digits=7, decimal_places=2)
    hora = models.TimeField()
    lugar = models.CharField(max_length=50)
    orden = models.ForeignKey(OrdenFlota, on_delete=models.CASCADE)

    def __str__(self):
        return f"Turno {self.turno} - Operador {self.codigo_operador.username} - Ruta {self.ruta.ruta}"


class Etapa(models.Model):
    nombre_etapa = models.CharField(max_length=50)
    cant_items = models.IntegerField()

    def __str__(self):
        return f"{self.nombre_etapa} - {self.cant_items} items"
    

class ItemChequeo(models.Model):
    nombre_item = models.CharField(max_length=100)
    etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre_item} - Etapa: {self.etapa.nombre_etapa}"
    

class detalle_chequeo(models.Model):
    orden = models.ForeignKey(OrdenFlota, on_delete=models.CASCADE)
    etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE)
    item = models.ForeignKey(ItemChequeo, on_delete=models.CASCADE)
    ESTADOS = [
        ('OK', 'OK'),
        ('P', 'Pendiente'),
    ]
    estado_item = models.CharField(max_length=2, choices=ESTADOS)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Detalle Chequeo - Orden: {self.orden.numero_bus} - Item: {self.item.nombre_item}"
    

class Inspeccion(models.Model):
    TIPOSALIDA = [
        ('P', 'Primera Salida'),
        ('S', 'Segunda Salida'),
        ('T', 'Tercera Salida'),
    ]
    salida = models.CharField(max_length=1, choices=TIPOSALIDA)
    nombre_inspector = models.ForeignKey(User, on_delete=models.CASCADE)
    hora = models.TimeField()
    observaciones = models.TextField(blank=True, null=True)
    firma = models.CharField(max_length=20)
    orden = models.ForeignKey(OrdenFlota, on_delete=models.CASCADE)

    def __str__(self):
        return f"Inspeccion - Orden: {self.orden.numero_bus} - Inspector: {self.nombre_inspector.username}"
    
    