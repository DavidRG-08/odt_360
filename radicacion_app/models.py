from django.db import models, transaction
from django.contrib.auth.models import User
from datetime import date
from django.db.models import F

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
    

class Entidad(models.Model):
    nombre = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.nombre}"


class ParametrosRadicacion(models.Model):
    prefijo = models.CharField(max_length=10)
    year = models.IntegerField()
    consecutivo = models.IntegerField()
    tipo_comunicacion = models.ForeignKey(TipoComunicacion, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name_plural = "Parámetros de Radicación"

    @transaction.atomic
    def obtener_siguiente_consecutivo(self):
        #Bloquear la fila para esta transaccion
        parametro = ParametrosRadicacion.objects.select_for_update().get(pk=self.pk)
        #guarda el valor actual
        consecutivo_actual = parametro.consecutivo

        #Incrementa el consecutivo
        parametro.consecutivo = F('consecutivo') + 1
        parametro.save(update_fields=['consecutivo'])

        return consecutivo_actual
    
    def generar_id_radicado(self):
        # Genera un ID unico y seguro
        consecutivo = self.obtener_siguiente_consecutivo()
        return f"{self.prefijo}-{self.year}-{self.tipo_comunicacion.id:02d}-{consecutivo:05d}"

    def __str__(self):
        return f"{self.prefijo} - {self.year} - {self.tipo_comunicacion.id} - {self.consecutivo}" 
    

class RadicacionEnviados(models.Model):
    id = models.CharField(max_length=20, primary_key=True) 
    fecha_radicacion = models.DateField(default=date.today)
    ENVIO = [
        ('Correo electronico', 'Correo electronico'),
        ('Fisico', 'Fisico'),
        ('Correo certificado', 'Correo certificado'), 
    ]

    medio_envio = models.CharField(max_length=50, choices=ENVIO)
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE)
    TYPE = [
        ('Interno', 'Interno'),
        ('Externo', 'Externo'),
    ]
    
    tipo_comunicacion = models.CharField(max_length=10, choices=TYPE)
    entidad = models.ForeignKey(Entidad, on_delete=models.CASCADE)
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
    recibido = models.CharField(max_length=30, blank=True, null=True)


    def __str__(self):
        return f"{self.id} - {self.asunto}"


class RadicacionRecibidos(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    fecha_radicacion = models.DateField(default=date.today)
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
    entidad = models.ForeignKey(Entidad, on_delete=models.CASCADE)
    asunto = models.CharField(max_length=200)
    anexos = models.IntegerField(default=0)
    responsable_por_responder = models.ForeignKey(Responsable, on_delete=models.CASCADE, related_name='responsable_por_responder')
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
    num_radicado_2025 = models.CharField(max_length=40, blank=True, null=True)


    def __str__(self):
        return f"{self.id} - {self.asunto}"


class RadicacionInternos(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    fecha_radicacion = models.DateField(default=date.today)
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
    entidad = models.ForeignKey(Entidad, on_delete=models.CASCADE)
    asunto = models.CharField(max_length=200)
    anexos = models.IntegerField()
    responsable_por_responder = models.ForeignKey(Responsable, on_delete=models.CASCADE, related_name='internos_por_responder')
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
    



# Tablas PQRSD

class CanalesRecepcion(models.Model):
    nombre = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return f"{self.nombre}"
    

class RutaVehiculo(models.Model):
    ruta = models.CharField(max_length=20, primary_key=True) 

    def __str__(self):
        return f"{self.ruta}"
    

class TipoPeticion(models.Model):
    nombre = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return f"{self.nombre}"
    

class Area(models.Model):
    nombre_area = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return f"{self.nombre_area}"
    

class Tipologia(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre}" 
    

class RadicadosRecibidosPqrsd(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    fecha_radicacion = models.DateField(default=date.today)
    radicador = models.ForeignKey(User , on_delete=models.CASCADE)
    tipo_radicado = models.CharField(max_length=10, default='PQRSD')
    UNIDAD = [
        ('Buses', 'Buses'),
        ('Cable', 'Cable')
    ]
    unidad_negocio = models.CharField(max_length=20, choices=UNIDAD)
    fecha_recibido_usuario = models.DateField()
    fecha_asignacion_traslado = models.DateField()
    radicado_recibido = models.CharField(max_length=40)
    canal_recepcion = models.ForeignKey(CanalesRecepcion, on_delete=models.CASCADE)
    tipo_peticion = models.ForeignKey(TipoPeticion, on_delete=models.CASCADE)
    nombre_remitente = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=200)
    email = models.EmailField()
    asunto = models.ForeignKey(Tipologia, on_delete=models.CASCADE)
    fecha_evento = models.DateField()
    hora_evento = models.TimeField()
    lugar_evento = models.CharField(max_length=200)
    serial_o_placa = models.CharField(max_length=20)
    ruta = models.ForeignKey(RutaVehiculo, on_delete=models.CASCADE)
    descripcion = models.TextField()
    asignado_a = models.ForeignKey(Area, on_delete=models.CASCADE)
    vencimiento_interno = models.DateField()
    vencimiento_por_ley = models.DateField()
    fecha_cierre = models.DateField(blank=True, null=True)
    ESTADO = [
        ('SI', 'SI'),
        ('NO', 'NO'),
        ('No Aplica', 'No Aplica'),
    ]
    culpabilidad = models.CharField(max_length=10, choices=ESTADO)
    OPE = [
        ('Operador', 'Operador'),
        ('Operadora', 'Operadora'),
        ('No Aplica', 'No Aplica'),
    ]
    operador = models.CharField(max_length=20, choices=OPE)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.id} - {self.asunto}"


class RadicadosEnviadosPqrsd(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    radicador = models.ForeignKey(User , on_delete=models.CASCADE)
    fecha_radicacion = models.DateField(default=date.today)
    tipo_radicado = models.CharField(max_length=10, default='PQRSD')
    asunto = models.CharField(max_length=200)
    radicado_asociado = models.ForeignKey(RadicadosRecibidosPqrsd, on_delete=models.CASCADE, blank=True, null=True)
    destinatario = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.id} - {self.asunto}"
