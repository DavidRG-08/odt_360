from datetime import timedelta

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.db import transaction
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from radicacion_app.models import AlertaRadicado


MAX_INTENTOS = 5
MINUTOS_BLOQUEO = 30


class Command(BaseCommand):
    help = 'Envía por correo las alertas de vencimiento pendientes.'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=100)

    def handle(self, *args, **options):
        limite = max(1, options['limit'])
        ahora = timezone.now()
        recuperadas = AlertaRadicado.objects.filter(
            estado=AlertaRadicado.Estado.PROCESANDO,
            procesando_desde__lt=ahora - timedelta(minutes=MINUTOS_BLOQUEO),
        ).update(
            estado=AlertaRadicado.Estado.PENDIENTE,
            procesando_desde=None,
            siguiente_intento_en=ahora,
            ultimo_error='Reintentada tras expirar el bloqueo de procesamiento.',
        )

        enviadas = fallidas = canceladas = procesadas = 0
        while procesadas < limite:
            alerta = self._reclamar_alerta()
            if alerta is None:
                break
            procesadas += 1

            if not self._sigue_elegible(alerta):
                self._cancelar(alerta)
                canceladas += 1
                continue

            try:
                self._enviar(alerta)
            except Exception as error:
                self._registrar_fallo(alerta, error)
                fallidas += 1
            else:
                AlertaRadicado.objects.filter(pk=alerta.pk).update(
                    estado=AlertaRadicado.Estado.ENVIADA,
                    enviada_en=timezone.now(),
                    procesando_desde=None,
                    ultimo_error='',
                )
                enviadas += 1

        self.stdout.write(self.style.SUCCESS(
            f'Enviadas: {enviadas}; fallidas: {fallidas}; canceladas: {canceladas}; '
            f'bloqueos recuperados: {recuperadas}.'
        ))

    @staticmethod
    def _reclamar_alerta():
        with transaction.atomic():
            alerta = AlertaRadicado.objects.select_for_update(skip_locked=True).filter(
                estado=AlertaRadicado.Estado.PENDIENTE,
                siguiente_intento_en__lte=timezone.now(),
                intentos__lt=MAX_INTENTOS,
            ).order_by('siguiente_intento_en', 'pk').first()
            if alerta is None:
                return None

            alerta.estado = AlertaRadicado.Estado.PROCESANDO
            alerta.procesando_desde = timezone.now()
            alerta.intentos += 1
            alerta.save(update_fields=['estado', 'procesando_desde', 'intentos'])
            return alerta

    @staticmethod
    def _sigue_elegible(alerta):
        radicado = alerta.radicado
        responsable = radicado.responsable_por_responder
        fecha_hoy = timezone.localdate()
        email_actual = (responsable.email or '').strip().lower()

        if (
            radicado.requiere_respuesta != 'SI'
            or radicado.fecha_respuesta is not None
            or radicado.respuesta_rad_interno_id is not None
            or radicado.estado_respuesta == 'Con Respuesta'
            or radicado.fecha_maxima_respuesta != alerta.fecha_limite
            or radicado.responsable_por_responder_id != alerta.responsable_id
            or email_actual != alerta.destinatario_email.strip().lower()
        ):
            return False

        if alerta.tipo == AlertaRadicado.Tipo.PROXIMO_VENCIMIENTO:
            return fecha_hoy <= alerta.fecha_limite <= fecha_hoy + timedelta(days=3)
        return alerta.tipo == AlertaRadicado.Tipo.VENCIDO and alerta.fecha_limite < fecha_hoy

    @staticmethod
    def _cancelar(alerta):
        AlertaRadicado.objects.filter(pk=alerta.pk).update(
            estado=AlertaRadicado.Estado.CANCELADA,
            procesando_desde=None,
            ultimo_error='El radicado cambió de estado, fecha límite o responsable antes del envío.',
        )

    @staticmethod
    def _enviar(alerta):
        radicado = alerta.radicado
        responsable = radicado.responsable_por_responder
        detalle_url = (
            settings.RADICACION_PUBLIC_BASE_URL
            + reverse('detalle_radicado_recibido', args=[radicado.pk])
        )
        contexto = {
            'radicado': radicado,
            'responsable': responsable,
            'detalle_url': detalle_url,
            'fecha_limite': alerta.fecha_limite,
        }
        proximo = alerta.tipo == AlertaRadicado.Tipo.PROXIMO_VENCIMIENTO
        prefijo = 'Próximo a vencer' if proximo else 'Radicado vencido'
        subject = f'{prefijo}: {radicado.pk}'
        text_body = render_to_string(
            'radicacion_app/emails/alerta_vencimiento.txt',
            {**contexto, 'proximo': proximo},
        )
        html_body = render_to_string(
            'radicacion_app/emails/alerta_vencimiento.html',
            {**contexto, 'proximo': proximo},
        )
        message = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[alerta.destinatario_email],
        )
        message.attach_alternative(html_body, 'text/html')
        message.send(fail_silently=False)

    @staticmethod
    def _registrar_fallo(alerta, error):
        agotados = alerta.intentos >= MAX_INTENTOS
        espera = min(60, 2 ** max(0, alerta.intentos - 1))
        AlertaRadicado.objects.filter(pk=alerta.pk).update(
            estado=(
                AlertaRadicado.Estado.FALLIDA
                if agotados else AlertaRadicado.Estado.PENDIENTE
            ),
            siguiente_intento_en=timezone.now() + timedelta(minutes=espera),
            procesando_desde=None,
            ultimo_error=str(error)[:4000],
        )