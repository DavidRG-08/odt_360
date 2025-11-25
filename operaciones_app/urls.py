from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    
    path('registro/', views.register ,name='registro'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<int:user_id>/', views.profile, name='profile'),
    path('home/', views.index, name='home'),

    # Operadores
    path('crear_operador/', views.crear_operador ,name='crear_operador'),
    path('lista_operadores/', views.lista_operadores, name='lista_operadores'),
    path('detalle_operador/<int:id>', views.detalle_operador, name='detalle_operador'),
    path('operadores_cv/', views.vista_hv_operador ,name='operadores_cv'),

    # enlaces para restablecer clave
    path('reset_password/', auth_views.PasswordResetView.as_view(), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # modulos de operaciones
    path('operaciones/', views.operaciones ,name='operaciones'),
    path('crear_solicitud/', views.crear_solicitud, name='crear_solicitud'),
    path('lista_solicitudes/', views.lista_solicitudes, name='lista_solicitudes'),
    path('solicitud/detalle/<int:solicitud_id>/', views.obtener_detalles_solicitud, name='detalle_solicitud'),
    path('solicitud/cancelar/<int:solicitud_id>/', views.cancelar_solicitud, name='cancelar_solicitud'),
    path('reporte_rutas/', views.generate_report_rutas, name='reporte_rutas'),

    # modulos de inspección
    # path('crear_orden_chequeo/', views.crear_orden_chequeo, name='crear_orden_chequeo'),
    # path('agregar_turno_inspeccion/<int:orden_id>/', views.agregar_turno_inspeccion, name='agregar_turno_inspeccion'),
    # path('lista_ordenes_chequeo/', views.listado_ordenes_chequeo, name='lista_ordenes_chequeo'),
    # path('inspeccion_turno/<int:orden_id>/', views.inspeccion_turno, name='inspeccion_turno'),
    # path('get-items-by-etapa/', views.get_items_by_etapa, name='get_items_by_etapa'),


]
