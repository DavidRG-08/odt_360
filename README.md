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
2. clonar el repositorio de GitHub
3. instalar las liberias del proyecto (requierements.txt)
4. Configuracion del proyecto en el servidor web 
5. Instalacion de la base de datos (PostgreSQL) 
6. Creacion de la base de datos 
7. crear el archivo con las variables de entorno 
8. crear la conexion entre el proyecto y la BD
9. Realizar la migracion de las tablas 
10. Ejecucion del script SQL con los datos a cargar para el funcionamiento de la app
11. Correr el proyecto
12. Pruebas de conexion