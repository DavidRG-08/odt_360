from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(TipoDocumento)
admin.site.register(Oficina)
admin.site.register(Responsable)
admin.site.register(ParametrosRadicacion)
admin.site.register(RadicacionEnviados)
admin.site.register(RadicacionRecibidos)
admin.site.register(TipoComunicacion)


