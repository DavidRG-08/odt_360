from django.contrib import admin
from .models import *

admin.site.register(SolicitudRuta)
admin.site.register(CancelacionRuta)
admin.site.register(Localidades)
admin.site.register(Ruta)
admin.site.register(Turno)
admin.site.register(Profile)
admin.site.register(EstadoRuta)

# admin.site.register(RutaFlota)
# admin.site.register(Etapa)
# admin.site.register(ItemChequeo)
