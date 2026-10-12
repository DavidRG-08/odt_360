import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


ALERT_DETECTION_FUNCTION = """
CREATE OR REPLACE FUNCTION radicacion_app_generar_alertas_vencimiento()
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    insertadas INTEGER;
    fecha_hoy DATE := (CURRENT_TIMESTAMP AT TIME ZONE 'America/Bogota')::DATE;
BEGIN
    INSERT INTO radicacion_app_alertaradicado (
        radicado_id,
        responsable_id,
        tipo,
        fecha_limite,
        destinatario_email,
        estado,
        intentos,
        creada_en,
        siguiente_intento_en,
        ultimo_error
    )
    SELECT
        radicado.id,
        responsable.id,
        CASE
            WHEN radicado.fecha_maxima_respuesta < fecha_hoy THEN 'vencido'
            ELSE 'proximo_vencimiento'
        END,
        radicado.fecha_maxima_respuesta,
        LOWER(BTRIM(responsable.email)),
        'pendiente',
        0,
        CURRENT_TIMESTAMP,
        CURRENT_TIMESTAMP,
        ''
    FROM radicacion_app_radicacionrecibidos AS radicado
    INNER JOIN radicacion_app_responsable AS responsable
        ON responsable.id = radicado.responsable_por_responder_id
    WHERE radicado.requiere_respuesta = 'SI'
      AND radicado.fecha_maxima_respuesta IS NOT NULL
      AND radicado.fecha_respuesta IS NULL
      AND radicado.respuesta_rad_interno_id IS NULL
      AND COALESCE(radicado.estado_respuesta, '') <> 'Con Respuesta'
      AND NULLIF(BTRIM(responsable.email), '') IS NOT NULL
      AND radicado.fecha_maxima_respuesta <= fecha_hoy + 3
    ON CONFLICT (radicado_id, tipo, fecha_limite, destinatario_email) DO NOTHING;

    GET DIAGNOSTICS insertadas = ROW_COUNT;
    RETURN insertadas;
END;
$$;
"""


class Migration(migrations.Migration):
    dependencies = [
        ('radicacion_app', '0018_trazabilidadcreacion_trazabilidadmodificacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='responsable',
            name='email',
            field=models.EmailField(blank=True, default='', max_length=254),
        ),
        migrations.CreateModel(
            name='AlertaRadicado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('proximo_vencimiento', 'Próximo a vencer'), ('vencido', 'Vencido')], max_length=24)),
                ('fecha_limite', models.DateField()),
                ('destinatario_email', models.EmailField(max_length=254)),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('procesando', 'Procesando'), ('enviada', 'Enviada'), ('fallida', 'Fallida'), ('cancelada', 'Cancelada')], default='pendiente', max_length=12)),
                ('intentos', models.PositiveSmallIntegerField(default=0)),
                ('creada_en', models.DateTimeField(default=django.utils.timezone.now)),
                ('siguiente_intento_en', models.DateTimeField(default=django.utils.timezone.now)),
                ('procesando_desde', models.DateTimeField(blank=True, null=True)),
                ('enviada_en', models.DateTimeField(blank=True, null=True)),
                ('ultimo_error', models.TextField(blank=True)),
                ('radicado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alertas_vencimiento', to='radicacion_app.radicacionrecibidos')),
                ('responsable', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='alertas_vencimiento', to='radicacion_app.responsable')),
            ],
            options={
                'ordering': ['creada_en'],
                'constraints': [models.UniqueConstraint(fields=('radicado', 'tipo', 'fecha_limite', 'destinatario_email'), name='rad_alerta_dedup_uq')],
                'indexes': [models.Index(fields=['estado', 'siguiente_intento_en'], name='rad_alerta_pendiente_idx')],
            },
        ),
        migrations.RunSQL(
            sql=ALERT_DETECTION_FUNCTION,
            reverse_sql='DROP FUNCTION IF EXISTS radicacion_app_generar_alertas_vencimiento();',
        ),
    ]