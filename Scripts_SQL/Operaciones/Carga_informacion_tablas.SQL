// Carga tabla Localidades 
INSERT INTO public.operaciones_app_localidades (id, nombre_localidad) VALUES (1, 'Antonio Nariño');
INSERT INTO public.operaciones_app_localidades (id, nombre_localidad) VALUES (2, 'Barrios Unidos');
INSERT INTO public.operaciones_app_localidades (id, nombre_localidad) VALUES (3, 'Bosa');
INSERT INTO public.operaciones_app_localidades (id, nombre_localidad) VALUES (4, 'Chapinero');
INSERT INTO public.operaciones_app_localidades (id, nombre_localidad) VALUES (5, 'Ciudad Bolívar');
INSERT INTO public.operaciones_app_localidades (id, nombre_localidad) VALUES (6, 'Engativá');
INSERT INTO public.operaciones_app_localidades (id, nombre_localidad) VALUES (7, 'Fontibón');
INSERT INTO public.operaciones_app_localidades (id, nombre_localidad) VALUES (8, 'Kennedy');
INSERT INTO public.operaciones_app_localidades (id, nombre_localidad) VALUES (9, 'La Candelaria');
INSERT INTO public.operaciones_app_localidades (id, nombre_localidad) VALUES (10, 'Los Mártires');
INSERT INTO public.operaciones_app_localidades (id, nombre_localidad) VALUES (11, 'Puente Aranda');
INSERT INTO public.operaciones_app_localidades (id, nombre_localidad) VALUES (12, 'Rafael Uribe Uribe');
INSERT INTO public.operaciones_app_localidades (id, nombre_localidad) VALUES (13, 'San Cristóbal');
INSERT INTO public.operaciones_app_localidades (id, nombre_localidad) VALUES (14, 'Santa Fe');
INSERT INTO public.operaciones_app_localidades (id, nombre_localidad) VALUES (15, 'Suba');
INSERT INTO public.operaciones_app_localidades (id, nombre_localidad) VALUES (16, 'Sumapaz');
INSERT INTO public.operaciones_app_localidades (id, nombre_localidad) VALUES (17, 'Teusaquillo');
INSERT INTO public.operaciones_app_localidades (id, nombre_localidad) VALUES (18, 'Tunjuelito');
INSERT INTO public.operaciones_app_localidades (id, nombre_localidad) VALUES (19, 'Usaquén');
INSERT INTO public.operaciones_app_localidades (id, nombre_localidad) VALUES (20, 'Usme');

// Carga tabla Rutas
INSERT INTO public.operaciones_app_ruta (id, ubicacion) VALUES (1, 'Norte');
INSERT INTO public.operaciones_app_ruta (id, ubicacion) VALUES (2, 'Sur');
INSERT INTO public.operaciones_app_ruta (id, ubicacion) VALUES (3, 'Soacha');

// Carga tabla turno
INSERT INTO public.operaciones_app_turno (id, name) VALUES (1, 'Entrada');
INSERT INTO public.operaciones_app_turno (id, name) VALUES (2, 'Salida');

// Carga tabla grupos
INSERT INTO public.auth_group (id, name) VALUES (1, 'Operador');
INSERT INTO public.auth_group (id, name) VALUES (2, 'Operaciones');

// Cargar superUsuario
INSERT INTO public.auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (1, 'pbkdf2_sha256$1000000$vqZrlyVHaEVP903NrddYsC$wf37/tevy411j/EfSQRiyH7ZTu2oWgqfbru/6LDeAIQ=', '2025-08-05 14:25:09.846292 +00:00', true, 'orfeo', '', '', '', true, true, '2025-07-20 16:07:45.280063 +00:00');
