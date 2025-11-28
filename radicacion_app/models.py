from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class TipoDocumento(models.Model):
    tipo = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.tipo}"
    

class Oficina(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre}"
    

class Responsable(models.Model):
    nombre = models.CharField(max_length=100)
    oficina = models.ForeignKey(Oficina, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} - {self.oficina.nombre}"
    

class TipoComunicacion(models.Model):
    id = models.IntegerField(primary_key=True)
    tipo = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.tipo}"


class ParametrosRadicacion(models.Model):
    prefijo = models.CharField(max_length=10)
    consecutivo = models.IntegerField()
    year = models.IntegerField()
    tipo_comunicacion = models.ForeignKey(TipoComunicacion, on_delete=models.CASCADE)
    contador = models.IntegerField()

    def __str__(self):
        return f"{self.prefijo} - {self.year} - {self.tipo_comunicacion.id} - {self.consecutivo}" 
    

class RadicacionEnviados(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    fecha_radicacion = models.DateField()
    medio_envio = models.CharField(max_length=50)
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE)
    TYPE = [
        ('Interno', 'Interno'),
        ('Externo', 'Externo'),
    ]
    
    tipo_comunicacion = models.CharField(max_length=10, choices=TYPE)
    entidad = models.CharField(max_length=100)
    asunto = models.CharField(max_length=200)
    num_rad_llegada = models.CharField(max_length=20, blank=True, null=True)
    num_rad_interno = models.CharField(max_length=20, blank=True, null=True)
    anexos = models.IntegerField()
    enviado_por = models.ForeignKey(Responsable, on_delete=models.CASCADE, related_name='enviado_por')
    oficina = models.ForeignKey(Oficina, on_delete=models.CASCADE)
    observaciones = models.TextField(blank=True, null=True)
    radicador = models.ForeignKey(User , on_delete=models.CASCADE)
    RESPUESTA = [
        ('SI', 'SI'),
        ('NO', 'NO'),
        ('N/A', 'N/A'),
        ('ANULADO', 'ANULADO'),
    ]

    requiere_respuesta = models.CharField(max_length=10, choices=RESPUESTA)
    tiempo_respuesta = models.IntegerField(blank=True, null=True)
    fecha_maxima_respuesta = models.DateField(blank=True, null=True)
    fecha_respuesta = models.DateField(blank=True, null=True)
    recibido = models.CharField(max_length=10, blank=True, null=True)


    def __str__(self):
        return f"{self.id} - {self.asunto}"


class RadicacionRecibidos(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    fecha_radicacion = models.DateField()
    INGRESO = [
        ('Correo electronico', 'Correo electronico'),
        ('Fisico', 'Fisico'),
        ('Correo certificado', 'Correo certificado'), 
    ]

    medio_ingreso = models.CharField(max_length=30, choices=INGRESO)
    TYPE = [
        ('Interno', 'Interno'),
        ('Externo', 'Externo'),
    ]
    
    tipo_comunicacion = models.CharField(max_length=10, choices=TYPE)
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE)
    num_rad_llegada = models.CharField(max_length=20, blank=True, null=True)
    entidad = models.CharField(max_length=100)
    asunto = models.CharField(max_length=200)
    anexos = models.IntegerField()
    Responsable_por_responder = models.ForeignKey(Responsable, on_delete=models.CASCADE, related_name='responsable_por_responder')
    oficina = models.ForeignKey(Oficina, on_delete=models.CASCADE)
    RESPUESTA = [
        ('SI', 'SI'),
        ('NO', 'NO'),
        ('TRAMITE INTERNO', 'TRAMITE INTERNO'),
    ]

    requiere_respuesta = models.CharField(max_length=20, choices=RESPUESTA)
    tiempo_respuesta = models.IntegerField(blank=True, null=True)
    fecha_maxima_respuesta = models.DateField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    radicador = models.ForeignKey(User , on_delete=models.CASCADE)
    respuesta_rad_interno = models.ForeignKey('RadicacionEnviados', on_delete=models.CASCADE, blank=True, null=True)
    RESPUESTA_ESTADO = [
        ('N/A', 'N/A'),
        ('Con Respuesta', 'Con Respuesta'),
        ('Sin Respuesta', 'Sin Respuesta'),
    ]
    
    estado_respuesta = models.CharField(max_length=20, choices=RESPUESTA_ESTADO, blank=True, null=True)    
    fecha_respuesta = models.DateField(blank=True, null=True)
    medio_respuesta = models.CharField(max_length=50, blank=True, null=True)


    def __str__(self):
        return f"{self.id} - {self.asunto}"
