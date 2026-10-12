# radicacion_app/tests.py
from datetime import timedelta
from io import StringIO
from unittest.mock import patch

from django.core import mail
from django.core.management import call_command
from django.test import TestCase, TransactionTestCase
from django.db import close_old_connections, transaction
from django.contrib.auth.models import Permission, User
from django.urls import reverse
from django.utils import timezone
from django.test import override_settings
from concurrent.futures import ThreadPoolExecutor
from .models import (
    AlertaRadicado,
    Area,
    CanalesRecepcion,
    Entidad,
    Oficina,
    ParametrosRadicacion,
    RadicacionEnviados,
    RadicacionInternos,
    RadicacionRecibidos,
    RadicadosEnviadosPqrsd,
    RadicadosRecibidosPqrsd,
    Responsable,
    RutaVehiculo,
    TipoDocumento,
    TipoComunicacion,
    TipoPeticion,
    Tipologia,
    TrazabilidadCreacion,
    TrazabilidadModificacion,
)
from .forms import CrearResponsableForm
from .reports import (
    ReporterExcelRadicadosEnviados,
    ReporterExcelRadicadosInternos,
    ReporterExcelRadicadosRecibidos,
    ReporterExcelPqrsdEnviados,
    ReporterExcelPqrsdRecibidos,
)
from .forms import (
    CrearRadicadoEnviadosForm,
    CrearRadicadoInternosForm,
    CrearRadicadoRecibidosForm,
    UpdateRadicadosEnviadosForm,
    UpdateRadicadosInternosForm,
    UpdateRadicadosRecibidosForm,
)


class FiltrosListadosRadicadosTest(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='filtros', password='test-password')
        permisos = Permission.objects.filter(codename__in=[
            'view_radicacionrecibidos',
            'view_radicacionenviados',
            'view_radicacioninternos',
        ])
        self.usuario.user_permissions.add(*permisos)
        self.client.force_login(self.usuario)

        self.oficina = Oficina.objects.create(nombre='Oficina Principal')
        self.otra_oficina = Oficina.objects.create(nombre='Oficina Alterna')
        self.responsable = Responsable.objects.create(
            nombre='Responsable',
            oficina=self.oficina,
        )
        self.tipo_documento = TipoDocumento.objects.create(tipo='Carta')
        self.entidad = Entidad.objects.create(nombre='Entidad de prueba')
        self.otra_entidad = Entidad.objects.create(nombre='Otra entidad')

    def test_filtra_recibidos_por_entidad_oficina_y_palabra_del_asunto(self):
        RadicacionRecibidos.objects.create(
            id='REC-001',
            medio_ingreso='Fisico',
            tipo_comunicacion='Externo',
            tipo_documento=self.tipo_documento,
            entidad=self.entidad,
            asunto='Reporte urgente de prueba',
            num_rad_llegada='EXT-REC-001',
            responsable_por_responder=self.responsable,
            oficina=self.oficina,
            requiere_respuesta='SI',
            radicador=self.usuario,
        )
        RadicacionRecibidos.objects.create(
            id='REC-002',
            medio_ingreso='Fisico',
            tipo_comunicacion='Externo',
            tipo_documento=self.tipo_documento,
            entidad=self.otra_entidad,
            asunto='Reporte de prueba',
            num_rad_llegada='EXT-REC-002',
            responsable_por_responder=self.responsable,
            oficina=self.otra_oficina,
            requiere_respuesta='SI',
            radicador=self.usuario,
        )

        response = self.client.get(reverse('lista_radicados_recibidos'), {
            'entidad': self.entidad.pk,
            'oficina': self.oficina.pk,
            'asunto': 'URGENTE',
            'num_rad_llegada': 'EXT-REC-001',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [radicado.pk for radicado in response.context['page_obj_recibidos']],
            ['REC-001'],
        )


class ResponsableActivoSelectionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='responsables', password='test-password')
        self.office = Oficina.objects.create(nombre='Oficina de prueba')
        self.active = Responsable.objects.create(
            nombre='Responsable activo',
            oficina=self.office,
            email='activo@example.com',
        )
        self.inactive = Responsable.objects.create(
            nombre='Responsable inactivo',
            oficina=self.office,
            email='inactivo@example.com',
            activo=False,
        )
        self.document_type = TipoDocumento.objects.create(tipo='Carta')
        self.entity = Entidad.objects.create(nombre='Entidad de prueba')

    def test_create_forms_only_offer_active_responsables(self):
        form_fields = (
            (CrearRadicadoRecibidosForm, 'responsable_por_responder'),
            (CrearRadicadoInternosForm, 'responsable_por_responder'),
            (CrearRadicadoEnviadosForm, 'enviado_por'),
        )

        for form_class, field_name in form_fields:
            with self.subTest(form=form_class.__name__):
                queryset = form_class().fields[field_name].queryset
                self.assertEqual(list(queryset.values_list('pk', flat=True)), [self.active.pk])

    def test_update_forms_keep_current_inactive_responsable_but_hide_other_inactive_ones(self):
        received = RadicacionRecibidos.objects.create(
            id='ACT-REC-001',
            medio_ingreso='Fisico',
            tipo_comunicacion='Externo',
            tipo_documento=self.document_type,
            entidad=self.entity,
            asunto='Recibido de prueba',
            responsable_por_responder=self.inactive,
            oficina=self.office,
            requiere_respuesta='SI',
            radicador=self.user,
        )
        internal = RadicacionInternos.objects.create(
            id='ACT-INT-001',
            medio_ingreso='Fisico',
            tipo_comunicacion='Interno',
            tipo_documento=self.document_type,
            entidad=self.entity,
            asunto='Interno de prueba',
            anexos=0,
            responsable_por_responder=self.inactive,
            oficina=self.office,
            requiere_respuesta='SI',
            radicador=self.user,
        )
        sent = RadicacionEnviados.objects.create(
            id='ACT-ENV-001',
            medio_envio='Fisico',
            tipo_documento=self.document_type,
            tipo_comunicacion='Interno',
            entidad=self.entity,
            asunto='Enviado de prueba',
            anexos=0,
            enviado_por=self.inactive,
            oficina=self.office,
            radicador=self.user,
            requiere_respuesta='NO',
        )
        form_instances = (
            (UpdateRadicadosRecibidosForm(instance=received), 'responsable_por_responder'),
            (UpdateRadicadosInternosForm(instance=internal), 'responsable_por_responder'),
            (UpdateRadicadosEnviadosForm(instance=sent), 'enviado_por'),
        )

        for form, field_name in form_instances:
            with self.subTest(form=form.__class__.__name__):
                field = form.fields[field_name]
                choices = list(field.queryset.values_list('pk', flat=True))
                self.assertCountEqual(choices, [self.active.pk, self.inactive.pk])
                self.assertEqual(field.label_from_instance(self.inactive), 'Responsable inactivo (inactivo; asignado actualmente)')


class FiltrosEnviadosInternosRadicadosTest(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='filtros-secundarios', password='test-password')
        permisos = Permission.objects.filter(codename__in=[
            'view_radicacionrecibidos',
            'view_radicacionenviados',
            'view_radicacioninternos',
        ])
        self.usuario.user_permissions.add(*permisos)
        self.client.force_login(self.usuario)

        self.oficina = Oficina.objects.create(nombre='Oficina Principal')
        self.otra_oficina = Oficina.objects.create(nombre='Oficina Alterna')
        self.responsable = Responsable.objects.create(
            nombre='Responsable',
            oficina=self.oficina,
        )
        self.tipo_documento = TipoDocumento.objects.create(tipo='Carta')
        self.entidad = Entidad.objects.create(nombre='Entidad de prueba')
        self.otra_entidad = Entidad.objects.create(nombre='Otra entidad')

    def test_filtra_enviados_por_entidad_oficina_y_palabra_del_asunto(self):
        RadicacionEnviados.objects.create(
            id='ENV-001',
            medio_envio='Fisico',
            tipo_documento=self.tipo_documento,
            tipo_comunicacion='Externo',
            entidad=self.entidad,
            asunto='Reporte urgente de prueba',
            num_rad_llegada='EXT-ENV-001',
            anexos=0,
            enviado_por=self.responsable,
            oficina=self.oficina,
            radicador=self.usuario,
            requiere_respuesta='SI',
        )
        RadicacionEnviados.objects.create(
            id='ENV-002',
            medio_envio='Fisico',
            tipo_documento=self.tipo_documento,
            tipo_comunicacion='Externo',
            entidad=self.otra_entidad,
            asunto='Reporte de prueba',
            num_rad_llegada='EXT-ENV-002',
            anexos=0,
            enviado_por=self.responsable,
            oficina=self.otra_oficina,
            radicador=self.usuario,
            requiere_respuesta='SI',
        )

        response = self.client.get(reverse('lista_radicados_enviados'), {
            'entidad': self.entidad.pk,
            'oficina': self.oficina.pk,
            'asunto': 'URGENTE',
            'num_rad_llegada': 'EXT-ENV-001',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [radicado.pk for radicado in response.context['page_obj_enviados']],
            ['ENV-001'],
        )

    def test_filtra_internos_por_entidad_oficina_y_palabra_del_asunto(self):
        RadicacionInternos.objects.create(
            id='INT-001',
            medio_ingreso='Fisico',
            tipo_documento=self.tipo_documento,
            tipo_comunicacion='Externo',
            entidad=self.entidad,
            asunto='Reporte urgente de prueba',
            num_rad_llegada='EXT-INT-001',
            anexos=0,
            responsable_por_responder=self.responsable,
            oficina=self.oficina,
            radicador=self.usuario,
            requiere_respuesta='SI',
        )
        RadicacionInternos.objects.create(
            id='INT-002',
            medio_ingreso='Fisico',
            tipo_documento=self.tipo_documento,
            tipo_comunicacion='Externo',
            entidad=self.otra_entidad,
            asunto='Reporte de prueba',
            num_rad_llegada='EXT-INT-002',
            anexos=0,
            responsable_por_responder=self.responsable,
            oficina=self.otra_oficina,
            radicador=self.usuario,
            requiere_respuesta='SI',
        )

        response = self.client.get(reverse('lista_radicados_internos'), {
            'entidad': self.entidad.pk,
            'oficina': self.oficina.pk,
            'asunto': 'URGENTE',
            'num_rad_llegada': 'EXT-INT-001',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [radicado.pk for radicado in response.context['page_obj_internos']],
            ['INT-001'],
        )


class DeteccionAlertasVencimientoTest(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='alertas', password='test-password')
        self.oficina = Oficina.objects.create(nombre='Oficina Alertas')
        self.responsable = Responsable.objects.create(
            nombre='Responsable Alertas',
            oficina=self.oficina,
            email='responsable@example.com',
        )
        tipo_documento = TipoDocumento.objects.create(tipo='Carta')
        entidad = Entidad.objects.create(nombre='Entidad alertas')
        self.fecha_hoy = timezone.localdate()

        RadicacionRecibidos.objects.create(
            id='ALR-PRONTO', medio_ingreso='Fisico', tipo_comunicacion='Externo',
            tipo_documento=tipo_documento, entidad=entidad, asunto='Vence pronto',
            responsable_por_responder=self.responsable, oficina=self.oficina,
            requiere_respuesta='SI', fecha_maxima_respuesta=self.fecha_hoy + timedelta(days=3),
            radicador=self.usuario,
        )
        RadicacionRecibidos.objects.create(
            id='ALR-VENCIDO', medio_ingreso='Fisico', tipo_comunicacion='Externo',
            tipo_documento=tipo_documento, entidad=entidad, asunto='Ya venció',
            responsable_por_responder=self.responsable, oficina=self.oficina,
            requiere_respuesta='SI', fecha_maxima_respuesta=self.fecha_hoy - timedelta(days=1),
            radicador=self.usuario,
        )
        RadicacionRecibidos.objects.create(
            id='ALR-RESPONDIDO', medio_ingreso='Fisico', tipo_comunicacion='Externo',
            tipo_documento=tipo_documento, entidad=entidad, asunto='Ya contestado',
            responsable_por_responder=self.responsable, oficina=self.oficina,
            requiere_respuesta='SI', fecha_maxima_respuesta=self.fecha_hoy - timedelta(days=1),
            fecha_respuesta=self.fecha_hoy, estado_respuesta='Con Respuesta',
            radicador=self.usuario,
        )

    def test_detection_creates_due_and_overdue_alerts_once(self):
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute('SELECT radicacion_app_generar_alertas_vencimiento()')
            first_insert_count = cursor.fetchone()[0]
            cursor.execute('SELECT radicacion_app_generar_alertas_vencimiento()')
            second_insert_count = cursor.fetchone()[0]

        self.assertEqual(first_insert_count, 2)
        self.assertEqual(second_insert_count, 0)
        self.assertEqual(AlertaRadicado.objects.count(), 2)
        self.assertEqual(
            set(AlertaRadicado.objects.values_list('radicado_id', 'tipo')),
            {
                ('ALR-PRONTO', AlertaRadicado.Tipo.PROXIMO_VENCIMIENTO),
                ('ALR-VENCIDO', AlertaRadicado.Tipo.VENCIDO),
            },
        )


class ResponsableEmailRequiredTest(TestCase):
    def test_new_responsible_requires_valid_email(self):
        form = CrearResponsableForm(data={
            'nombre': 'Responsable nuevo',
            'oficina': 1,
            'email': '',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class EntregaAlertasVencimientoTest(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='correo-alerta', password='test-password')
        self.oficina = Oficina.objects.create(nombre='Oficina Alertas')
        self.responsable = Responsable.objects.create(
            nombre='Responsable Alertas',
            oficina=self.oficina,
            email='responsable@example.com',
        )
        self.radicado = RadicacionRecibidos.objects.create(
            id='ALR-CORREO',
            medio_ingreso='Fisico',
            tipo_comunicacion='Externo',
            tipo_documento=TipoDocumento.objects.create(tipo='Carta'),
            entidad=Entidad.objects.create(nombre='Entidad correo'),
            asunto='Solicitud de información',
            responsable_por_responder=self.responsable,
            oficina=self.oficina,
            requiere_respuesta='SI',
            fecha_maxima_respuesta=timezone.localdate() + timedelta(days=3),
            radicador=self.usuario,
        )
        self.alerta = AlertaRadicado.objects.create(
            radicado=self.radicado,
            responsable=self.responsable,
            tipo=AlertaRadicado.Tipo.PROXIMO_VENCIMIENTO,
            fecha_limite=self.radicado.fecha_maxima_respuesta,
            destinatario_email=self.responsable.email,
        )

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='notificaciones@example.com',
        RADICACION_PUBLIC_BASE_URL='https://odt.example.com',
    )
    def test_sends_email_and_marks_alert_sent(self):
        call_command('enviar_alertas_radicados', stdout=StringIO())

        self.alerta.refresh_from_db()
        self.assertEqual(self.alerta.estado, AlertaRadicado.Estado.ENVIADA)
        self.assertEqual(self.alerta.intentos, 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['responsable@example.com'])
        self.assertIn('ALR-CORREO', mail.outbox[0].subject)
        self.assertIn('https://odt.example.com/radicados_recibidos/detalle/ALR-CORREO/', mail.outbox[0].alternatives[0][0])

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='notificaciones@example.com',
        RADICACION_PUBLIC_BASE_URL='https://odt.example.com',
    )
    def test_cancels_alert_if_radicado_is_answered_before_delivery(self):
        self.radicado.fecha_respuesta = timezone.localdate()
        self.radicado.estado_respuesta = 'Con Respuesta'
        self.radicado.save(update_fields=['fecha_respuesta', 'estado_respuesta'])

        call_command('enviar_alertas_radicados', stdout=StringIO())

        self.alerta.refresh_from_db()
        self.assertEqual(self.alerta.estado, AlertaRadicado.Estado.CANCELADA)
        self.assertEqual(mail.outbox, [])

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='notificaciones@example.com',
        RADICACION_PUBLIC_BASE_URL='https://odt.example.com',
    )
    @patch('radicacion_app.management.commands.enviar_alertas_radicados.EmailMultiAlternatives.send', side_effect=OSError('SMTP no disponible'))
    def test_email_failure_is_retried_and_error_is_recorded(self, send_email):
        call_command('enviar_alertas_radicados', stdout=StringIO())

        self.alerta.refresh_from_db()
        self.assertEqual(self.alerta.estado, AlertaRadicado.Estado.PENDIENTE)
        self.assertEqual(self.alerta.intentos, 1)
        self.assertIn('SMTP no disponible', self.alerta.ultimo_error)
        self.assertGreater(self.alerta.siguiente_intento_en, timezone.now())


class ConsecutivoSeguroTest(TransactionTestCase):
    """Test para verificar que los consecutivos sean únicos incluso con usuarios simultáneos"""
    
    def setUp(self):
        # TipoComunicacion.id es IntegerField(primary_key=True) sin autoincremento:
        # hay que asignarlo explícitamente.
        tipo = TipoComunicacion.objects.create(id=1, tipo="Comunicaciones recibidas")

        self.parametro = ParametrosRadicacion.objects.create(
            prefijo='ODT',
            year=2025,
            tipo_comunicacion= tipo,
            consecutivo=100
        )
    
    def test_consecutivos_unicos_concurrentes(self):
        """Verifica que con 10 threads simultáneos todos obtengan IDs únicos"""
        ids_generados = []
        
        def generar_id():
            try:
                id_generado = self.parametro.generar_id_radicado()
                ids_generados.append(id_generado)
            finally:
                # Cada hilo abre su propia conexión; hay que cerrarla para
                # que PostgreSQL permita eliminar la BD de pruebas al final.
                close_old_connections()
        
        # Ejecutar 10 threads simultáneamente
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(generar_id) for _ in range(10)]
            for future in futures:
                future.result()
        
        # Verificar que todos sean únicos
        self.assertEqual(len(ids_generados), len(set(ids_generados)))
        print(f"✓ IDs generados: {ids_generados}")


class TrazabilidadEdicionPqrsdTest(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='auditor', password='test-password')
        permiso = Permission.objects.get(codename='change_radicadosrecibidospqrsd')
        permiso_ver = Permission.objects.get(codename='view_radicadosrecibidospqrsd')
        self.usuario.user_permissions.add(permiso, permiso_ver)

        canal = CanalesRecepcion.objects.create(nombre='Web')
        tipo_peticion = TipoPeticion.objects.create(nombre='Queja')
        tipologia = Tipologia.objects.create(nombre='Servicio')
        ruta = RutaVehiculo.objects.create(ruta='R1')
        area = Area.objects.create(nombre_area='Operaciones')
        self.radicado = RadicadosRecibidosPqrsd.objects.create(
            id='PQR-TEST-1',
            radicador=self.usuario,
            fecha_recibido_usuario='2026-09-28',
            fecha_asignacion_traslado='2026-09-28',
            radicado_recibido='EXT-001',
            canal_recepcion=canal,
            tipo_peticion=tipo_peticion,
            nombre_remitente='Nombre inicial',
            telefono='3001234567',
            direccion='Calle 1',
            email='persona@example.com',
            asunto=tipologia,
            lugar_evento='Centro',
            serial_o_placa='NA',
            ruta=ruta,
            descripcion='Descripción inicial',
            asignado_a=area,
            vencimiento_interno='2026-10-05',
            vencimiento_por_ley='2026-10-13',
            culpabilidad='No Aplica',
            operador='No Aplica',
        )

    def test_edicion_registra_campos_modificados(self):
        self.client.force_login(self.usuario)
        response = self.client.post(
            reverse('editar_radicado_pqrsd', args=[self.radicado.pk]),
            {
                'unidad_negocio': 'Buses',
                'fecha_recibido_usuario': '2026-09-28',
                'fecha_asignacion_traslado': '2026-09-28',
                'radicado_recibido': 'EXT-001',
                'canal_recepcion': 'Web',
                'tipo_peticion': 'Queja',
                'nombre_remitente': 'Nombre actualizado',
                'telefono': '3001234567',
                'direccion': 'Calle 1',
                'email': 'persona@example.com',
                'asunto': str(self.radicado.asunto_id),
                'fecha_evento': '',
                'hora_evento': '',
                'lugar_evento': 'Centro',
                'serial_o_placa': 'NA',
                'ruta': 'R1',
                'descripcion': 'Descripción inicial',
                'asignado_a': 'Operaciones',
                'vencimiento_interno': '2026-10-05',
                'vencimiento_por_ley': '2026-10-13',
                'fecha_cierre': '',
                'culpabilidad': 'No Aplica',
                'operador': 'No Aplica',
                'observaciones': '',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.radicado.refresh_from_db()
        self.assertEqual(self.radicado.nombre_remitente, 'Nombre actualizado')

        trazabilidad = TrazabilidadModificacion.objects.get(object_id=self.radicado.pk)
        self.assertEqual(trazabilidad.usuario, self.usuario)
        self.assertEqual(
            trazabilidad.campos_modificados['nombre_remitente'],
            {'anterior': 'Nombre inicial', 'nuevo': 'Nombre actualizado'},
        )

    def test_historial_muestra_creacion_modificacion_y_regreso_al_listado(self):
        TrazabilidadCreacion.objects.create(
            usuario=self.usuario,
            radicado=self.radicado,
        )
        TrazabilidadModificacion.objects.create(
            usuario=self.usuario,
            radicado=self.radicado,
            campos_modificados={
                'nombre_remitente': {
                    'anterior': 'Nombre inicial',
                    'nuevo': 'Nombre actualizado',
                },
            },
        )
        self.client.force_login(self.usuario)

        response = self.client.get(
            reverse('trazabilidad_radicado', args=['recibido-pqrsd', self.radicado.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Creación')
        self.assertContains(response, 'Modificación')
        self.assertContains(response, 'Nombre actualizado')
        self.assertContains(response, reverse('lista_radicados_pqrsd'))


class RadicadoDetailAccessTest(TestCase):
    def test_detail_views_require_module_permissions(self):
        user = User.objects.create_user(username='other-module-user', password='test-password')
        self.client.force_login(user)
        detail_urls = [
            reverse('detalle_radicado_recibido', args=['REC-UNKNOWN']),
            reverse('detalle_radicado_enviado', args=['ENV-UNKNOWN']),
            reverse('detalle_radicado_interno', args=['INT-UNKNOWN']),
            reverse('detalle_radicado_pqrsd', args=['PQR-UNKNOWN']),
            reverse('detalle_radicado_enviado_pqrsd', args=['PQR-ENV-UNKNOWN']),
        ]

        for url in detail_urls:
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertEqual(response.status_code, 403)


class RadicadoReportQueryBehaviorTest(TestCase):
    def test_empty_queryset_remains_empty_for_each_export(self):
        reports_and_models = [
            (ReporterExcelRadicadosRecibidos, RadicacionRecibidos),
            (ReporterExcelRadicadosEnviados, RadicacionEnviados),
            (ReporterExcelRadicadosInternos, RadicacionInternos),
            (ReporterExcelPqrsdRecibidos, RadicadosRecibidosPqrsd),
            (ReporterExcelPqrsdEnviados, RadicadosEnviadosPqrsd),
        ]

        for reporter_class, model in reports_and_models:
            with self.subTest(reporter=reporter_class.__name__):
                reporter = reporter_class(model.objects.none())

                self.assertFalse(reporter.queryset.exists())

    def test_export_ignores_none_string_filters(self):
        user = User.objects.create_user(username='export-user', password='test-password')
        permission = Permission.objects.get(
            codename='view_radicacionenviados',
            content_type__app_label='radicacion_app',
        )
        user.user_permissions.add(permission)
        self.client.force_login(user)

        response = self.client.get(reverse('reporte_radicados_enviados'), {
            'start_date_rad': '',
            'end_date_rad': '',
            'entidad': 'None',
            'asunto': '',
            'oficina': 'None',
            'radicado': 'None',
            'num_rad_llegada': '',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

    def test_internal_export_ignores_none_string_filters(self):
        user = User.objects.create_user(username='internal-export-user', password='test-password')
        permission = Permission.objects.get(
            codename='view_radicacioninternos',
            content_type__app_label='radicacion_app',
        )
        user.user_permissions.add(permission)
        self.client.force_login(user)

        response = self.client.get(reverse('reporte_radicados_internos'), {
            'start_date_rad': '',
            'end_date_rad': '',
            'entidad': 'None',
            'asunto': '',
            'oficina': 'None',
            'radicado': 'None',
            'num_rad_llegada': '',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )