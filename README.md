# Aplicacion ODT_360

## 1 modulo - Operaciones (Ruta acercamiento)

### Descripcion de la aplicacion

> El objetivo de este modulo, es para llevar el control de la ruta de acercamiento que actualmente tienen los operadores y puedan facilitar su forma de realizar la solicitud de ruta.

este compuesto del perfil operador y operaciones.

* Operador: perfil por el cual ingresa los operadores. cuentan con los permisos para solicitar una nueva ruta cada vez que lo requieran y tambien pueden cancelarla.
ellos tendran un usuario de acceso a la aplicacion, el cual quedara registrado todo con su usuario, ademas podran consultar sus solicitudes.

* Operaciones: Perfil orientado al area de operaciones, el cual puede administrar las rutas solicitadas por los operadores. Adicionalmente pueden crear nuevos operadores que ingresen a la empresa.
tambien pueden editar la informacion correspondiente a cada operador, puede ver un listado de todos los operadores registrados y ver a detalle la informacion. filtrar la informacion para una mejor y facil busqueda.
cuentan con la vista para ver todas las solicitudes y filtrarlas por un rango de fechas y ver el estado en el que se encuentran, como descargar la informacion en un reporte excel. 



## Contenido del Repositorio 

1. Carpeta con el proyecto - odt_360
2. archivo .gitignore 
3. requirements.txt (Librerias)
4. Carpeta Scripts_SQL - Script carga_informacion_tablas.sql




## Pasos a tener en cuenta para el despliegue

1. Montar un servidor web (Apache, NGNIX, IIS)
2. Python version 3.13 o superior
3. clonar el repositorio de GitHub
4. instalar las liberias del proyecto (requierements.txt)
5. Configuracion del proyecto en el servidor web 
6. Instalacion de la base de datos (PostgreSQL) 
7. Creacion de la base de datos 
8. crear el archivo con las variables de entorno (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` y `DB_NAME`, `DB_USER`, `DB_PWD`, `DB_HOST`, `DB_PORT`)
9. crear la conexion entre el proyecto y la BD
10. Realizar la migracion de las tablas 
11. Ejecucion del script SQL con los datos a cargar para el funcionamiento de la app
12. Correr el proyecto
13. Pruebas de conexion

En producción, configura `DEBUG=False`, define `ALLOWED_HOSTS` con los dominios reales separados por comas y sirve el sitio exclusivamente por HTTPS. Las cookies de sesión y CSRF se marcan como seguras automáticamente cuando `DEBUG=False`.

## Alertas de vencimiento de radicados

La detección de alertas administrativas usa `fecha_maxima_respuesta` y solo considera radicados que requieren respuesta y siguen sin respuesta. Crea una alerta próxima para fechas entre hoy y los próximos tres días, y una alerta vencida para fechas anteriores. El outbox evita repetir el mismo aviso para radicado, tipo, fecha límite y destinatario.

Configura estas variables de entorno para el correo:

- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`
- `EMAIL_USE_TLS` o `EMAIL_USE_SSL`, `DEFAULT_FROM_EMAIL`
- `RADICACION_PUBLIC_BASE_URL` con la URL pública de ODT 360

Pasos de despliegue:

1. Aplicar migraciones con `python manage.py migrate`.
2. Completar y validar el correo de cada responsable desde el administrador de Django. Los responsables sin correo se omiten en la detección.
3. Para PostgreSQL con `pg_cron`, un DBA debe habilitar la extensión y configurar `cron.timezone = 'America/Bogota'`; luego ejecutar `Scripts_SQL/Radicacion/Programar_alertas_radicados.sql` con el usuario de conexión de ODT 360, que será el rol que ejecute la función.
4. Programar el comando de envío en el host cada cinco minutos para entregar alertas pendientes: `*/5 * * * * /ruta/venv/bin/python /ruta/proyecto/manage.py enviar_alertas_radicados --limit 100`.
5. Si el proveedor no permite `pg_cron`, programar `python manage.py generar_alertas_radicados` una vez al día en el cron del host y mantener el comando de envío cada cinco minutos.

Para validar en staging, usar primero `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`, ejecutar `python manage.py generar_alertas_radicados` y `python manage.py enviar_alertas_radicados`, y revisar los estados/error en `AlertaRadicado` desde Django Admin. Cambia al backend SMTP solo después de verificar destinatarios y contenido.