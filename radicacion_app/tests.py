# radicacion_app/tests.py
from django.test import TestCase, TransactionTestCase
from django.db import transaction
from django.contrib.auth.models import Permission, User
from django.urls import reverse
from concurrent.futures import ThreadPoolExecutor
from .models import (
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
from .reports import (
    ReporterExcelRadicadosEnviados,
    ReporterExcelRadicadosInternos,
    ReporterExcelRadicadosRecibidos,
    ReporterExcelPqrsdEnviados,
    ReporterExcelPqrsdRecibidos,
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


class ConsecutivoSeguroTest(TransactionTestCase):
    """Test para verificar que los consecutivos sean únicos incluso con usuarios simultáneos"""
    
    def setUp(self):
        tipo = TipoComunicacion.objects.create(tipo="Comunicaciones recibidas")

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
            id_generado = self.parametro.generar_id_radicado()
            ids_generados.append(id_generado)
        
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