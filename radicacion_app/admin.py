from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(TipoDocumento)
admin.site.register(Oficina)
admin.site.register(ParametrosRadicacion)
admin.site.register(TipoComunicacion)
admin.site.register(Entidad)
admin.site.register(CanalesRecepcion)
admin.site.register(RutaVehiculo)
admin.site.register(TipoPeticion)
admin.site.register(Area)
admin.site.register(Tipologia)


@admin.register(Responsable)
class ResponsableAdmin(admin.ModelAdmin):
	list_display = ('nombre', 'oficina', 'email', 'activo')
	list_filter = ('activo', 'oficina')
	list_editable = ('activo',)
	search_fields = ('nombre', 'email', 'oficina__nombre')


@admin.register(AlertaRadicado)
class AlertaRadicadoAdmin(admin.ModelAdmin):
	list_display = ('radicado', 'tipo', 'fecha_limite', 'destinatario_email', 'estado', 'intentos', 'creada_en')
	list_filter = ('tipo', 'estado', 'fecha_limite')
	search_fields = ('radicado__id', 'destinatario_email', 'responsable__nombre')
	readonly_fields = ('creada_en', 'enviada_en', 'procesando_desde', 'ultimo_error')

