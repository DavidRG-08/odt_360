from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta



class Estado(models.Model):
    nombre = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.nombre}"


class Etapa(models.Model):
    nombre = models.CharField(max_length=30)
    cant_items = models.IntegerField()

    def __str__(self):
        return f"{self.nombre}" 


class Vehiculo(models.Model):
    vehiculo_id = models.CharField(primary_key=True, max_length=10)

    def __str__(self):
        return f"{self.vehiculo_id}"
    

class OrdenAlistamiento(models.Model):
    vehiculo = models.ForeignKey(Vehiculo,on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, default=1)
    fecha_creacion_orden = models.DateField(default=datetime.today().strftime('%Y-%m-%d'))
    fecha_inicio = models.DateTimeField(blank=True, null=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    tiempo_alistamiento = models.IntegerField(blank=True, null=True)
    novedades = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        #Calcular duracion si ambos campos estan completos
        if self.fecha_inicio and self.fecha_fin:
            start_datetime =  datetime.combine(datetime.min.date(), self.fecha_inicio.time())
            end_datetime = datetime.combine(datetime.min.date(), self.fecha_fin.time())
            
            # Si fecha fin es menor que fecha inicio, asumimos que cruza la medianoche
            if end_datetime < start_datetime:
                end_datetime += timedelta(days=1)
            
            delta = end_datetime - start_datetime
            self.tiempo_alistamiento = int(delta.total_seconds()/60)
        else:
            self.tiempo_alistamiento = 0
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id}" + "--" + f"{self.user_id}" + "--" + f"{self.vehiculo_id}"
     

class EtapaInspeccion(models.Model):
    orden = models.ForeignKey(OrdenAlistamiento, on_delete=models.CASCADE)
    etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    total_items = models.IntegerField()
    progreso = models.FloatField(default=0.0)
    fecha_inicio = models.DateTimeField(blank=True, null=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    tiempo_inspeccion = models.IntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        #Calcular duracion si ambos campos estan completos
        if self.fecha_inicio and self.fecha_fin:
            start_datetime =  datetime.combine(datetime.min.date(), self.fecha_inicio.time())
            end_datetime = datetime.combine(datetime.min.date(), self.fecha_fin.time())
            
            # Si fecha fin es menor que fecha inicio, asumimos que cruza la medianoche
            if end_datetime < start_datetime:
                end_datetime += timedelta(days=1)
            
            delta = end_datetime - start_datetime

            self.tiempo_inspeccion = int(delta.total_seconds()/60)
        else:
            self.tiempo_inspeccion = 0
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id}" + " -- " + f"{self.orden_id}" + " -- " + f"{self.etapa}" + " -- " + f"{self.estado}" + " -- " + f"{self.progreso}"
    

class ItemInspeccion(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=100)
    etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.nombre}"


class DetalleInspeccion(models.Model):
    orden = models.ForeignKey(OrdenAlistamiento, on_delete=models.CASCADE)
    etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE)
    item = models.ForeignKey(ItemInspeccion, on_delete=models.CASCADE)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    observaciones = models.TextField(blank=True, null=True)
    fecha_inicio = models.DateTimeField(blank=True, null=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.id}" + " -- " + f"{self.estado}" + " -- " + f"{self.item}" + " -- " + f"{self.fecha_inicio}" + " -- " + f"{self.fecha_fin}"
    


    
