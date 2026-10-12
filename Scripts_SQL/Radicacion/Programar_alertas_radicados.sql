-- El DBA habilita pg_cron y cron.timezone = 'America/Bogota'.
-- Ejecutar el scheduling como el usuario de conexión de ODT 360.
CREATE EXTENSION IF NOT EXISTS pg_cron;

SELECT cron.unschedule(jobid)
FROM cron.job
WHERE jobname = 'odt360-radicacion-alertas-diarias';

SELECT cron.schedule(
    'odt360-radicacion-alertas-diarias',
    '0 6 * * *',
    'SELECT radicacion_app_generar_alertas_vencimiento();'
);