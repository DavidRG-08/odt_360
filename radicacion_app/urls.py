from django.urls import path
from . import views


urlpatterns = [
    path('radicacion/', views.radicacion, name='radicacion'),
    path('radicados_recibidos/', views.menu_radicados_recibidos_view, name='radicados_recibidos'),
    path('crear_radicados_recibidos/', views.radicados_recibidos_view, name='crear_radicados_recibidos'),
    path('crear_radicados_pqrsd/', views.radicados_recibidos_pqrsd_view, name='crear_radicados_pqrsd'),
    path('crear_radicados_enviados/', views.radicados_enviados_view, name='crear_radicados_enviados'),
    path('crear_radicados_internos/', views.radicados_internos_view, name='crear_radicados_internos'),

    # APIs para cálculo de fechas
    path('api/festivos-colombia/', views.get_festivos_colombia, name='get_festivos_colombia'),
    path('api/calcular-fecha-respuesta/', views.calcular_fecha_respuesta, name='calcular_fecha_respuesta'),

    # API para obtener oficina del responsable
    path('api/get-oficina-responsable/', views.get_oficina_responsable, name='get_oficina_responsable'),

]

