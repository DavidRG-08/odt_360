from concurrent.futures import ThreadPoolExecutor
from django.contrib.auth.models import Permission, User
from django.db import close_old_connections
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse
from threading import Barrier
from .models import DetalleInspeccion, Estado, Etapa, EtapaInspeccion, ItemInspeccion, OrdenAlistamiento, Vehiculo
from .reports import ReporterExcelOrdenesAlistamiento


class MaintenanceReportAccessTest(TestCase):
	def test_report_requires_view_permission(self):
		user = User.objects.create_user(username='operator', password='test-password')
		self.client.force_login(user)

		response = self.client.get(reverse('reporte_ordenes'))

		self.assertEqual(response.status_code, 403)

	def test_csv_upload_requires_add_permission(self):
		user = User.objects.create_user(username='operator', password='test-password')
		self.client.force_login(user)

		response = self.client.get(reverse('cargar_orden'))

		self.assertEqual(response.status_code, 403)


class MaintenanceMutationAccessTest(TestCase):
	def setUp(self):
		self.owner = User.objects.create_user(username='owner', password='test-password')
		self.other_user = User.objects.create_user(username='other', password='test-password')
		permission = Permission.objects.get(
			codename='change_ordenalistamiento',
			content_type__app_label='mantenimiento_app',
		)
		self.owner.user_permissions.add(permission)
		self.other_user.user_permissions.add(permission)
		self.open_state = Estado.objects.create(nombre='Abierta')
		self.process_state = Estado.objects.create(nombre='En proceso')
		self.finished_state = Estado.objects.create(nombre='Finalizada')
		self.order = OrdenAlistamiento.objects.create(
			user=self.owner,
			vehiculo=Vehiculo.objects.create(vehiculo_id='BUS-1'),
			estado=self.open_state,
		)

	def test_user_cannot_start_another_users_order(self):
		self.client.force_login(self.other_user)

		response = self.client.post(reverse('iniciar_orden', args=[self.order.pk]))

		self.assertEqual(response.status_code, 404)

	def test_mutation_requires_csrf_token(self):
		client = Client(enforce_csrf_checks=True)
		client.force_login(self.other_user)

		response = client.post(reverse('iniciar_orden', args=[self.order.pk]))

		self.assertEqual(response.status_code, 403)

	def test_user_cannot_start_second_order_before_finishing_first(self):
		second_order = OrdenAlistamiento.objects.create(
			user=self.owner,
			vehiculo=Vehiculo.objects.create(vehiculo_id='BUS-2'),
			estado=self.open_state,
		)
		self.client.force_login(self.owner)

		first_response = self.client.post(reverse('iniciar_orden', args=[self.order.pk]))
		second_response = self.client.post(reverse('iniciar_orden', args=[second_order.pk]))

		self.assertEqual(first_response.status_code, 200)
		self.assertEqual(second_response.status_code, 409)
		self.assertEqual(second_response.json()['code'], 'another_order_in_progress')
		second_order.refresh_from_db()
		self.assertIsNone(second_order.fecha_inicio)

	def test_cannot_start_stage_on_another_order_while_one_is_active(self):
		second_order = OrdenAlistamiento.objects.create(
			user=self.owner,
			vehiculo=Vehiculo.objects.create(vehiculo_id='BUS-2'),
			estado=self.open_state,
		)
		self.client.force_login(self.owner)
		self.client.post(reverse('iniciar_orden', args=[self.order.pk]))

		response = self.client.post(reverse(
			'iniciar_inspeccion_etapa',
			args=[second_order.pk, 'Mecanica'],
		))

		self.assertEqual(response.status_code, 409)
		self.assertEqual(response.json()['code'], 'order_not_active')

	def test_finishing_last_item_completes_stage_and_order(self):
		stage = Etapa.objects.create(nombre='Mecanica', cant_items=1)
		item = ItemInspeccion.objects.create(
			nombre='Frenos',
			descripcion='Revisar frenos',
			etapa=stage,
		)
		stage_inspection = EtapaInspeccion.objects.create(
			orden=self.order,
			etapa=stage,
			estado=self.open_state,
			total_items=1,
		)
		detail = DetalleInspeccion.objects.create(
			orden=self.order,
			etapa=stage,
			item=item,
			estado=self.open_state,
		)
		self.client.force_login(self.owner)
		self.client.post(reverse('iniciar_orden', args=[self.order.pk]))

		response = self.client.post(reverse('finalizar_item', args=[detail.pk]))

		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.json()['orden_finalizada'])
		self.order.refresh_from_db()
		stage_inspection.refresh_from_db()
		self.assertEqual(self.order.estado, self.finished_state)
		self.assertIsNotNone(self.order.fecha_fin)
		self.assertEqual(stage_inspection.estado, self.finished_state)
		self.assertIsNotNone(stage_inspection.fecha_fin)


class ConcurrentOrderStartTest(TransactionTestCase):
	reset_sequences = True

	def setUp(self):
		self.technician = User.objects.create_user(username='concurrent-tech', password='test-password')
		permission = Permission.objects.get(
			codename='change_ordenalistamiento',
			content_type__app_label='mantenimiento_app',
		)
		self.technician.user_permissions.add(permission)
		self.open_state = Estado.objects.create(nombre='Abierta')
		Estado.objects.create(nombre='En proceso')
		Estado.objects.create(nombre='Finalizada')
		self.orders = [
			OrdenAlistamiento.objects.create(
				user=self.technician,
				vehiculo=Vehiculo.objects.create(vehiculo_id=f'BUS-{number}'),
				estado=self.open_state,
			)
			for number in (10, 11)
		]

	def test_simultaneous_starts_allow_only_one_active_order(self):
		clients = [Client(), Client()]
		for client in clients:
			client.force_login(self.technician)
		barrier = Barrier(2)

		def start_order(client, order):
			close_old_connections()
			try:
				barrier.wait(timeout=10)
				response = client.post(reverse('iniciar_orden', args=[order.pk]))
				return response.status_code
			finally:
				close_old_connections()

		with ThreadPoolExecutor(max_workers=2) as executor:
			responses = list(executor.map(
				lambda pair: start_order(*pair),
				zip(clients, self.orders),
			))

		self.assertCountEqual(responses, [200, 409])
		self.assertEqual(
			OrdenAlistamiento.objects.filter(user=self.technician, estado__nombre='En proceso').count(),
			1,
		)


class MaintenanceReportQueryBehaviorTest(TestCase):
	def test_empty_queryset_remains_empty(self):
		reporter = ReporterExcelOrdenesAlistamiento(OrdenAlistamiento.objects.none())

		self.assertFalse(reporter.queryset.exists())
