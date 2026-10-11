from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Group  # para filtrar por grupo en permisos
from django.db import transaction
from django.core.paginator import Paginator
from django.contrib import messages
from datetime import datetime
from django.utils.timezone import now
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from .models import *
from .forms import *
from .reports import ReporterExcelOrdenesAlistamiento
import json
import csv
from io import TextIOWrapper
from utils import obtener_modulos_visibles




def _ordenes_visibles(user):
    ordenes = OrdenAlistamiento.objects.all()
    if not user.is_superuser and not user.groups.filter(name__in=['Mtto_admin', 'Mtto_view']).exists():
        ordenes = ordenes.filter(user=user)
    return ordenes


def _orden_para_edicion(user, orden_id):
    ordenes = OrdenAlistamiento.objects.all()
    if not user.is_superuser and not user.groups.filter(name='Mtto_admin').exists():
        ordenes = ordenes.filter(user=user)
    return get_object_or_404(ordenes, id=orden_id)


def _detalle_para_edicion(user, detalle_id):
    detalles = DetalleInspeccion.objects.select_related('orden')
    if not user.is_superuser and not user.groups.filter(name='Mtto_admin').exists():
        detalles = detalles.filter(orden__user=user)
    return get_object_or_404(detalles, id=detalle_id)


def _otra_orden_en_proceso(orden):
    estado_proceso = get_object_or_404(Estado, nombre='En proceso')
    return OrdenAlistamiento.objects.filter(
        user_id=orden.user_id,
        estado=estado_proceso,
        fecha_fin__isnull=True,
    ).exclude(pk=orden.pk)


def _error_si_orden_no_activa(orden):
    estado_proceso = get_object_or_404(Estado, nombre='En proceso')
    if orden.estado_id != estado_proceso.pk or not orden.fecha_inicio or orden.fecha_fin:
        return JsonResponse({
            'success': False,
            'error': 'La orden no está en proceso. Iníciala antes de trabajar sus etapas.',
            'code': 'order_not_active',
        }, status=409)

    otra_orden = _otra_orden_en_proceso(orden).first()
    if otra_orden:
        return JsonResponse({
            'success': False,
            'error': f'El técnico ya tiene la orden #{otra_orden.pk} en proceso.',
            'code': 'another_order_in_progress',
        }, status=409)

    return None


# Modulo Mantenimiento
@login_required
def mantenimiento(request):
    MODULOS_MANTENIMIENTO = [
        {
            'nombre': 'Crear Orden de Alistamiento',
            'url': 'crear_orden',
            'icono': 'fa-plus-circle',
            'grupos': ['Mtto_admin']
        },
        {
            'nombre': 'Consultar Ordenes de Alistamiento',
            'url': 'consultar_ordenes',
            'icono': 'fa-list',
            'grupos': ['Mtto_admin', 'Mtto_view', 'Mtto_user', 'Tecnicos_mtto']
        },
        {
            'nombre': 'Vehiculos',
            'url': 'consultar_vehiculos',
            'icono': 'fa-bus',
            'grupos': ['Mtto_admin', 'Mtto_view']
        },
        {
            'nombre': 'Ver detalle de Etapas e Ítems',
            'url': 'ver_detalle_etapas',
            'icono': 'fa-tasks',
            'grupos': ['Mtto_admin', 'Mtto_view', 'Tecnicos_mtto']
        },
    ]
    modulos = obtener_modulos_visibles(MODULOS_MANTENIMIENTO, request.user)
    return render(request, 'mantenimiento_app/mantenimiento.html', {'modulos': modulos})


# Vista para crear ordenes 
@login_required
@permission_required('mantenimiento_app.add_ordenalistamiento', raise_exception=True)    
def crear_orden(request):
    if request.method == 'POST':
        form = CrearOrdenForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Orden creada con exito!")

            return redirect('consultar_ordenes')
        
        else:
            print("Error de formulario", form.errors)
            messages.error(request, "Hubo un error al momento de crear la orden!")
    
    else:
        form = CrearOrdenForm()
    
    return render(request, 'mantenimiento_app/crear_orden.html', {'form': form})


# Crear orden masiva
@login_required
@permission_required('mantenimiento_app.add_ordenalistamiento', raise_exception=True)
def cargar_csv(request):
    form = CsvUploadForm()

    if request.method == 'POST':
        form = CsvUploadForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo_csv']
            archivo_wrapper = TextIOWrapper(archivo.file, encoding='utf-8')
            lector = csv.reader(archivo_wrapper)

            exitosos = 0
            errores = []

            for fila in lector:
                # Verificar que la fila tenga al menos dos columnas
                if len(fila) >=2:
                    try:
                        vehiculo_id = fila[0]
                        user_id = int(fila[1])

                        vehiculo = Vehiculo.objects.filter(vehiculo_id=vehiculo_id).first()
                        user = User.objects.filter(id=user_id).first()

                        if vehiculo and user:
                            OrdenAlistamiento.objects.create(
                                vehiculo = vehiculo,
                                user = user
                            )
                            exitosos += 1
                        else:
                            errores.append(f"Vehiculo o usuario no encontrados: {fila}")

                    except ValueError as e:
                        errores.append(f"Error al convertir los datos: {fila}, error{e}")
                else:
                    errores.append(f"Fila ignorada (incompleta) {fila}")
            
            if errores:
                messages.error(request, f"Se presentaron errores en la carga: {errores}")
            elif exitosos > 0:
                messages.success(request, f"Se cargaron {exitosos} ordenes con exito!")

            return redirect('consultar_ordenes')
    
    return render(request, 'mantenimiento_app/cargar_csv.html', {'form': form}) 

    
# Consultar ordenes de alistamiento
@login_required
@permission_required('mantenimiento_app.view_ordenalistamiento', raise_exception=True)
def consultar_ordenes(request):
    ordenes = OrdenAlistamiento.objects.all().order_by('-id')
    estados = Estado.objects.all()

    # Filtrar por estado
    estado_id = request.GET.get('estado')
    if estado_id:
        ordenes = ordenes.filter(estado_id=estado_id)

    # filtrar segun el grupo de usuario
    if not request.user.groups.filter(name='Mtto_admin').exists() and not request.user.groups.filter(name='Mtto_view').exists():
        ordenes = ordenes.filter(user=request.user)

    # Rango de fechas
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # filtro en un rango de fechas
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            ordenes = ordenes.filter(
                fecha_creacion_orden__gte = start_date, 
                fecha_creacion_orden__lte = end_date
            )
        except ValueError:
            pass

    paginator = Paginator(ordenes, 20)
    page_number = request.GET.get('page')
    page_obj_ord = paginator.get_page(page_number)

    return render(request, 'mantenimiento_app/lista_ordenes.html', {
        'page_obj_ord': page_obj_ord,
        'estados': estados,
        'selected_estado': estado_id,
        'start_date': start_date,
        'end_date': end_date
        })


@login_required
@permission_required('mantenimiento_app.add_ordenalistamiento', raise_exception=True)
def agregar_ot(request, pk):
    instancia = get_object_or_404(OrdenAlistamiento, pk=pk)
    if request.method == 'POST':
        form = FormUpdateOrden(request.POST, instance=instancia)
        if form.is_valid():
            form.save()
            messages.success(request, "Orden de trabajo agregada con exito!")
            return redirect('consultar_ordenes')
    
    else:
        form = FormUpdateOrden(instance=instancia)


    return render(request, 'mantenimiento_app/agregar_ot.html', {'form': form})




# Ver detalle de cada orden
@login_required
@permission_required('mantenimiento_app.view_ordenalistamiento', raise_exception=True)
def visualizar_orden(request, id):
    orden = get_object_or_404(_ordenes_visibles(request.user), id=id)
    return render(request, "mantenimiento_app/visualizar_orden.html", {"orden": orden})


@login_required
@permission_required('mantenimiento_app.view_ordenalistamiento', raise_exception=True)
@ensure_csrf_cookie
def detalle_orden(request, orden_id):
    orden = get_object_or_404(_ordenes_visibles(request.user), id=orden_id)
    etapas = EtapaInspeccion.objects.filter(orden=orden)
    if not etapas.exists():
        messages.error(request, "No hay etapas de inspeccion para esta orden!")
    es_admin_mtto = request.user.groups.filter(name='Mtto_admin').exists()
    puede_trabajar_orden = (
        request.user.has_perm('mantenimiento_app.change_ordenalistamiento')
        and not es_admin_mtto
    )
    orden_en_proceso = None
    if puede_trabajar_orden:
        orden_en_proceso = OrdenAlistamiento.objects.filter(
            user=request.user,
            estado__nombre='En proceso',
            fecha_inicio__isnull=False,
            fecha_fin__isnull=True,
        ).exclude(pk=orden.pk).first()

    return render(request, "mantenimiento_app/detalle_orden.html", {
        "etapas": etapas,
        "orden": orden,
        "es_admin_mtto": es_admin_mtto,
        "puede_trabajar_orden": puede_trabajar_orden,
        "orden_en_proceso": orden_en_proceso,
    })

@login_required
@permission_required('mantenimiento_app.view_ordenalistamiento', raise_exception=True)
def generar_reporte_ordenes(request):
    # Obtiene los filtros de fecha
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    estado_id = request.GET.get('estado')

    # Consulta para filtrar las ordenes
    queryset = _ordenes_visibles(request.user)

    if start_date and end_date:
        queryset = queryset.filter(
            fecha_creacion_orden__gte=start_date, 
            fecha_creacion_orden__lte=end_date
        )
    if estado_id:
        queryset = queryset.filter(estado_id=estado_id)
    
    # Generar el reporte 
    report = ReporterExcelOrdenesAlistamiento(queryset)
    return report.get(request)




@require_POST
@permission_required('mantenimiento_app.change_ordenalistamiento', raise_exception=True)
def iniciar_orden(request, orden_id):
    """Inicia una orden, serializando los inicios para el técnico asignado."""
    with transaction.atomic():
        orden = _orden_para_edicion(request.user, orden_id)
        User.objects.select_for_update().get(pk=orden.user_id)
        orden = OrdenAlistamiento.objects.select_for_update().get(pk=orden.pk)
        estado_proceso = get_object_or_404(Estado, nombre='En proceso')
        estado_finalizada = get_object_or_404(Estado, nombre='Finalizada')

        if orden.fecha_fin or orden.estado_id == estado_finalizada.pk:
            return JsonResponse({
                "success": False,
                "error": "La orden ya está finalizada y no se puede iniciar de nuevo.",
                "code": "order_already_finished",
            }, status=409)

        otra_orden = _otra_orden_en_proceso(orden).first()
        if otra_orden:
            return JsonResponse({
                "success": False,
                "error": f"El técnico ya tiene la orden #{otra_orden.pk} en proceso. Finalízala antes de iniciar otra.",
                "code": "another_order_in_progress",
            }, status=409)

        if not orden.fecha_inicio:
            orden.fecha_inicio = now()
        orden.estado = estado_proceso
        orden.save(update_fields=['fecha_inicio', 'estado', 'tiempo_alistamiento'])

        return JsonResponse({
            "success": True,
            "fecha_inicio": orden.fecha_inicio.strftime("%Y-%m-%d %H:%M:%S")
        })
    

@require_POST
@permission_required('mantenimiento_app.change_ordenalistamiento', raise_exception=True)
@transaction.atomic
def iniciar_inspeccion_etapa(request, orden_id, etapa_nombre):
    """Inicia la inspección de la etapa especificada"""
    orden = _orden_para_edicion(request.user, orden_id)
    User.objects.select_for_update().get(pk=orden.user_id)
    orden = OrdenAlistamiento.objects.select_for_update().get(pk=orden.pk)
    error = _error_si_orden_no_activa(orden)
    if error:
        return error

    etapa_obj = get_object_or_404(Etapa, nombre=etapa_nombre)
    etapa_inspeccion = get_object_or_404(EtapaInspeccion, orden=orden, etapa=etapa_obj)
    estado_finalizada = get_object_or_404(Estado, nombre='Finalizada')
    if etapa_inspeccion.estado_id == estado_finalizada.pk:
        return JsonResponse({
            'success': False,
            'error': 'La etapa ya está finalizada.',
            'code': 'stage_already_finished',
        }, status=409)

    if not etapa_inspeccion.fecha_inicio:
        etapa_inspeccion.fecha_inicio = now()
        etapa_inspeccion.estado = get_object_or_404(Estado, nombre='En proceso')
        etapa_inspeccion.save()

    return JsonResponse({
        "success": True,
        "fecha_inicio": etapa_inspeccion.fecha_inicio.strftime("%Y-%m-%d %H:%M:%S"),
        "etapa": etapa_nombre
    })


@require_POST
@permission_required('mantenimiento_app.change_ordenalistamiento', raise_exception=True)
@transaction.atomic
def actualizar_observaciones(request):
    """ Actualiza las observaciones de una inspección """
    data = json.loads(request.body)
    inspeccion = _detalle_para_edicion(request.user, data["inspeccion_id"])
    User.objects.select_for_update().get(pk=inspeccion.orden.user_id)
    orden = OrdenAlistamiento.objects.select_for_update().get(pk=inspeccion.orden_id)
    error = _error_si_orden_no_activa(orden)
    if error:
        return error

    inspeccion.observaciones = data["observaciones"]
    inspeccion.save(update_fields=['observaciones'])
    return JsonResponse({"success": True})


@require_POST
@permission_required('mantenimiento_app.change_ordenalistamiento', raise_exception=True)
@transaction.atomic
def finalizar_item(request, item_id):
    """ Marca la finalización del item con la fecha y hora actual """
    item = _detalle_para_edicion(request.user, item_id)
    User.objects.select_for_update().get(pk=item.orden.user_id)
    orden = OrdenAlistamiento.objects.select_for_update().get(pk=item.orden_id)
    item = DetalleInspeccion.objects.select_for_update().get(pk=item.pk)
    error = _error_si_orden_no_activa(orden)
    if error:
        return error

    estado_finalizada = get_object_or_404(Estado, nombre='Finalizada')
    if not item.fecha_fin:
        item.fecha_fin = now()
        item.estado = estado_finalizada
        item.save()

    items_pendientes_etapa = DetalleInspeccion.objects.filter(
        orden=orden,
        etapa=item.etapa,
    ).exclude(estado=estado_finalizada)
    if not items_pendientes_etapa.exists():
        etapa = get_object_or_404(EtapaInspeccion, orden=orden, etapa=item.etapa)
        etapa.estado = estado_finalizada
        if not etapa.fecha_fin:
            etapa.fecha_fin = now()
        etapa.save()

    items_pendientes_orden = DetalleInspeccion.objects.filter(orden=orden).exclude(
        estado=estado_finalizada,
    )
    orden_finalizada = not items_pendientes_orden.exists()
    if orden_finalizada:
        orden.estado = estado_finalizada
        if not orden.fecha_fin:
            orden.fecha_fin = now()
        orden.save()

    return JsonResponse({
        "fecha_fin": item.fecha_fin.strftime("%Y-%m-%d %H:%M:%S"),
        "estado": item.estado.nombre,
        "orden_finalizada": orden_finalizada,
    })


# detalle orden mecanica
@login_required
@permission_required('mantenimiento_app.change_ordenalistamiento', raise_exception=True)
@ensure_csrf_cookie
def trabajar_orden_mecanica(request, orden_id):
    orden = _orden_para_edicion(request.user, orden_id)
    inspecciones = DetalleInspeccion.objects.filter(orden=orden, etapa=1)

    es_admin_mtto = request.user.groups.filter(name='Mtto_admin').exists()
    return render(request, "mantenimiento_app/trabaja_orden.html", {"inspecciones": inspecciones, "orden": orden, "es_admin_mtto": es_admin_mtto})


# detalle orden externa
@login_required
@permission_required('mantenimiento_app.change_ordenalistamiento', raise_exception=True)
@ensure_csrf_cookie
def trabajar_orden_externa(request, orden_id):
    orden = _orden_para_edicion(request.user, orden_id)
    inspecciones = DetalleInspeccion.objects.filter(orden=orden, etapa=2)

    es_admin_mtto = request.user.groups.filter(name='Mtto_admin').exists()
    return render(request, "mantenimiento_app/trabaja_orden.html", {"inspecciones": inspecciones, "orden": orden, "es_admin_mtto": es_admin_mtto})


# detalle orden interna
@login_required
@permission_required('mantenimiento_app.change_ordenalistamiento', raise_exception=True)
@ensure_csrf_cookie
def trabajar_orden_interna(request, orden_id):
    orden = _orden_para_edicion(request.user, orden_id)
    inspecciones = DetalleInspeccion.objects.filter(orden=orden, etapa=3)

    es_admin_mtto = request.user.groups.filter(name='Mtto_admin').exists()
    return render(request, "mantenimiento_app/trabaja_orden.html", {"inspecciones": inspecciones, "orden": orden, "es_admin_mtto": es_admin_mtto})


# detalle orden electrica
@login_required
@permission_required('mantenimiento_app.change_ordenalistamiento', raise_exception=True)
@ensure_csrf_cookie
def trabajar_orden_electrica(request, orden_id):
    orden = _orden_para_edicion(request.user, orden_id)
    inspecciones = DetalleInspeccion.objects.filter(orden=orden, etapa=4)

    es_admin_mtto = request.user.groups.filter(name='Mtto_admin').exists()
    return render(request, "mantenimiento_app/trabaja_orden.html", {"inspecciones": inspecciones, "orden": orden, "es_admin_mtto": es_admin_mtto})


@login_required
@permission_required('mantenimiento_app.view_etapa', raise_exception=True)
def ver_detalle_etapas(request):
    etapas = Etapa.objects.all()
    items_por_etapa = {}
    items_inspeccion = ItemInspeccion.objects.all()

    for etapa in etapas:
        items_por_etapa[etapa.id] = items_inspeccion.filter(etapa_id=etapa)

    return render(
        request, 
        "mantenimiento_app/ver_detalle_etapas.html", 
        {
            "etapas": etapas, 
            "items_por_etapa": items_por_etapa
        }
    )



@login_required
@permission_required('mantenimiento_app.add_vehiculo', raise_exception=True)
def vehiculos(request):
    if request.method == "POST":
        form = CrearVehiculoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Vehículo creado con éxito!")
            return redirect('consultar_vehiculos')
    else:
        form = CrearVehiculoForm()
    return render(request, 'mantenimiento_app/crear_vehiculos.html', {'form': form})



@login_required
@permission_required('mantenimiento_app.view_vehiculo', raise_exception=True)
def consultar_vehiculos(request):
    vehiculos = Vehiculo.objects.all()

    vehiculo = request.GET.get('vehiculo')
    if vehiculo:
        vehiculos = vehiculos.filter(vehiculo_id__icontains=vehiculo)

    return render(request, 'mantenimiento_app/consultar_vehiculos.html', {'vehiculos': vehiculos})


