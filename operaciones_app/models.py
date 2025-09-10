from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


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
    

class SolicitudRuta(models.Model):
    fecha_solicitud = models.DateTimeField(default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
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
    estado = models.BooleanField(default=True, blank=True)

    def __str__(self):
        return f"{self.operador}" + f"{self.fecha_solicitud}"
    

class CancelacionRuta(models.Model):
    fecha_cancelacion = models.DateTimeField()
    operador = models.CharField(max_length=10)
    descripcion = models.TextField()

    def __str__(self):
        return f"{self.operador}"
    

