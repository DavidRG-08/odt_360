from django.urls import path 
from . import views

urlpatterns = [
    path('mantenimiento/', views.mantenimiento ,name='mantenimiento'),
    path('crear_orden/', views.crear_orden, name='crear_orden'),
    path('cargar_orden/', views.cargar_csv, name='cargar_orden'),
    path('consultar_ordenes/', views.consultar_ordenes, name='consultar_ordenes'),
    path('reporte_ordenes/', views.generar_reporte_ordenes, name='reporte_ordenes'),
    path('ver_orden/<int:id>', views.visualizar_orden, name='ver_orden'),
    path('detalle_orden/<int:orden_id>', views.detalle_orden, name='detalle_orden'),


    path('trabaja_orden_mec/<int:orden_id>', views.trabajar_orden_mecanica, name='trabaja_orden_mec'),
    path('trabaja_orden_ext/<int:orden_id>', views.trabajar_orden_externa, name='trabaja_orden_ext'),
    path('trabaja_orden_int/<int:orden_id>', views.trabajar_orden_interna, name='trabaja_orden_int'),
    path('trabaja_orden_ele/<int:orden_id>', views.trabajar_orden_electrica, name='trabaja_orden_ele'),

    # URLs para iniciar inspecciones por etapa generica
    path('iniciar_inspeccion/<int:orden_id>/<str:etapa_nombre>/', views.iniciar_inspeccion_etapa, name='iniciar_inspeccion_etapa'),

    path("iniciar_orden/<int:orden_id>/", views.iniciar_orden, name="iniciar_orden"),
    path("actualizar_observaciones/", views.actualizar_observaciones, name="actualizar_observaciones"),
    path("finalizar_item/<int:item_id>/", views.finalizar_item, name="finalizar_item"),

    path("ver_etapas/", views.ver_detalle_etapas, name="ver_detalle_etapas"),
    path("crear_vehiculo/", views.vehiculos, name="crear_vehiculo"),
    path("consultar_vehiculos/", views.consultar_vehiculos, name="consultar_vehiculos"),

]