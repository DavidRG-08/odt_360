from django.urls import path
from . import views


urlpatterns = [
    path('radicacion/', views.radicacion, name='radicacion'),
    path('radicados_administrativos/', views.menu_radicados_administrativos, name='radicados_administrativos'),
    path('radicacion_pqrsd/', views.radicacion_pqrsd, name='radicacion_pqrsd'),
    path('radicados_recibidos/', views.menu_radicados_recibidos, name='radicados_recibidos'),
    path('radicados_enviados/', views.menu_radicados_enviados, name='radicados_enviados'),
    path('radicados_internos/', views.menu_radicados_internos, name='radicados_internos'),

    path('crear_radicados_recibidos/', views.crear_radicados_recibidos, name='crear_radicados_recibidos'),
    path('lista_radicados_recibidos/', views.view_radicados_recibidos, name='lista_radicados_recibidos'),
    path('radicados_recibidos/detalle/<str:radicado_id>/', views.obtener_detalle_rad_recibido, name='detalle_radicado_recibido'),
    path('radicados_recibidos/editar/<str:radicado_id>/', views.editar_radicado_recibido, name='editar_radicado_recibido'),

    path('crear_radicados_enviados/', views.crear_radicados_enviados, name='crear_radicados_enviados'),
    path('lista_radicados_enviados/', views.view_radicados_enviados, name='lista_radicados_enviados'),
    path('radicados_enviados/detalle/<str:radicado_id>/', views.obtener_detalle_rad_enviado, name='detalle_radicado_enviado'),

    path('crear_radicados_internos/', views.crear_radicados_internos, name='crear_radicados_internos'),
    path('lista_radicados_internos/', views.view_radicados_internos, name='lista_radicados_internos'),
    path('radicados_internos/detalle/<str:radicado_id>/', views.obtener_detalle_rad_interno, name='detalle_radicado_interno'),

    # PQRSD
    path('crear_radicado_pqrsd/', views.crear_radicados_recibidos_pqrsd, name='crear_radicado_pqrsd'),
    path('lista_radicados_pqrsd/', views.view_radicados_recibidos_pqrsd, name='lista_radicados_pqrsd'),
    path('pqrsd/detalle/<str:radicado_id>/', views.obtener_detalle_pqrsd_recibido, name='detalle_radicado_pqrsd'),
    path('pqrsd/editar/<str:radicado_id>/', views.editar_pqrsd_recibido, name='editar_radicado_pqrsd'),

    # APIs para cálculo de fechas
    path('api/festivos-colombia/', views.get_festivos_colombia, name='get_festivos_colombia'),
    path('api/calcular-fecha-respuesta/', views.calcular_fecha_respuesta, name='calcular_fecha_respuesta'),

    # API para obtener oficina del responsable
    path('api/get-oficina-responsable/', views.get_oficina_responsable, name='get_oficina_responsable'),

    # APIs para cálculo de vencimientos
    path('api/calcular-vencimientos-pqrsd/', views.calcular_vencimientos_pqrsd, name='calcular_vencimientos_pqrsd'),

    # Menú de propiedades administrativas
    path('propiedades/', views.menu_propiedades, name='propiedades'),
    path('propiedades/oficinas/', views.view_oficina, name='lista_oficinas'),
    path('propiedades/oficina/crear_oficina/', views.crear_oficina, name='crear_oficina'),
    path('propiedades/entidades/', views.view_entidades, name='lista_entidades'),
    path('propiedades/entidad/crear_entidad/', views.crear_entidad, name='crear_entidad'),
    path('propiedades/responsable/', views.view_responsable, name='lista_responsables'),
    path('propiedades/responsable/crear_responsable/', views.crear_responsable, name='crear_responsable'),
    path('propiedades/tipo_documento/', views.view_tipo_documento, name='lista_tipo_documentos'),
    path('propiedades/tipo_documento/crear_tipo_documento/', views.crear_tipo_documento, name='crear_tipo_documento'),


]

