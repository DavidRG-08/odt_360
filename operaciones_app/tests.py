from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now
from operaciones_app.models import EstadoRuta, Localidades, Ruta, SolicitudRuta, Turno
from operaciones_app.reports import ReporterExcelRutas


class UserRegistrationAccessTest(TestCase):
	def test_anonymous_user_cannot_register(self):
		response = self.client.get(reverse('registro'))

		self.assertEqual(response.status_code, 302)
		self.assertEqual(User.objects.count(), 0)

	def test_authenticated_user_without_permission_is_forbidden(self):
		user = User.objects.create_user(username='operator', password='test-password')
		self.client.force_login(user)

		response = self.client.get(reverse('registro'))

		self.assertEqual(response.status_code, 403)


class ReportQueryBehaviorTest(TestCase):
	def test_empty_queryset_remains_empty(self):
		reporter = ReporterExcelRutas(SolicitudRuta.objects.none())

		self.assertFalse(reporter.queryset.exists())


class SolicitudObjectAccessTest(TestCase):
	def setUp(self):
		self.owner = User.objects.create_user(username='owner1', password='test-password')
		self.other_user = User.objects.create_user(username='other1', password='test-password')
		permissions = Permission.objects.filter(
			content_type__app_label='operaciones_app',
			codename__in=['view_solicitudruta', 'add_solicitudruta'],
		)
		self.other_user.user_permissions.add(*permissions)
		self.solicitud = SolicitudRuta.objects.create(
			operador=self.owner.username,
			telefono='3001234567',
			turno=Turno.objects.create(name='Entrada'),
			fecha_recogida=now(),
			localidad=Localidades.objects.create(nombre_localidad='Centro'),
			barrio='Centro',
			ubicacion='https://maps.example.com/location',
			ruta=Ruta.objects.create(ubicacion='Norte'),
			direccion='Calle 1',
			usuario=self.owner,
			estado=EstadoRuta.objects.create(estado='Activa'),
		)

	def test_user_cannot_open_another_users_request(self):
		self.client.force_login(self.other_user)

		response = self.client.get(reverse('detalle_solicitud', args=[self.solicitud.pk]))

		self.assertEqual(response.status_code, 404)

	def test_user_cannot_cancel_another_users_request(self):
		self.client.force_login(self.other_user)

		response = self.client.post(
			reverse('cancelar_solicitud', args=[self.solicitud.pk]),
			{'descripcion': 'No autorizado'},
		)

		self.assertEqual(response.status_code, 404)

	def test_user_with_add_user_permission_can_open_registration(self):
		user = User.objects.create_user(username='admin', password='test-password')
		permission = Permission.objects.get(
			codename='add_user',
			content_type__app_label='auth',
		)
		user.user_permissions.add(permission)
		self.client.force_login(user)

		response = self.client.get(reverse('registro'))

		self.assertEqual(response.status_code, 200)

	def test_report_requires_view_permission(self):
		user = User.objects.create_user(username='operator', password='test-password')
		self.client.force_login(user)

		response = self.client.get(reverse('reporte_rutas'))

		self.assertEqual(response.status_code, 403)
