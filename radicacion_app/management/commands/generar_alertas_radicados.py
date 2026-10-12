from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Q
from django.utils import timezone

from radicacion_app.models import RadicacionRecibidos


class Command(BaseCommand):
    help = 'Crea alertas de vencimiento para radicados recibidos administrativos.'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute('SELECT radicacion_app_generar_alertas_vencimiento()')
            insertadas = cursor.fetchone()[0]

        fecha_hoy = timezone.localdate()
        sin_correo = RadicacionRecibidos.objects.filter(
            requiere_respuesta='SI',
            fecha_respuesta__isnull=True,
            respuesta_rad_interno__isnull=True,
            fecha_maxima_respuesta__lte=fecha_hoy + timedelta(days=3),
        ).exclude(estado_respuesta='Con Respuesta').filter(
            Q(responsable_por_responder__email='')
            | Q(responsable_por_responder__email__isnull=True)
        ).count()

        self.stdout.write(self.style.SUCCESS(f'Alertas nuevas: {insertadas}.'))
        if sin_correo:
            self.stderr.write(self.style.WARNING(
                f'{sin_correo} radicados elegibles no tienen correo de responsable.'
            ))