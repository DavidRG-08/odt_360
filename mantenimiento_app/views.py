from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Group  # para filtrar por grupo en permisos
from django.core.paginator import Paginator
from django.contrib import messages
from datetime import datetime
from django.utils.timezone import now
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
from .forms import *
from .reports import ReporterExcelOrdenesAlistamiento
import json
import csv
from io import TextIOWrapper


# Modulo Mantenimiento
@login_required
def mantenimiento(request):
    return render(request, 'mantenimiento_app/mantenimiento.html')


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
    orden = get_object_or_404(OrdenAlistamiento, id=id)
    return render(request, "mantenimiento_app/visualizar_orden.html", {"orden": orden})


@login_required
@permission_required('mantenimiento_app.view_ordenalistamiento', raise_exception=True)
def detalle_orden(request, orden_id):
    etapas = EtapaInspeccion.objects.filter(orden_id=orden_id)
    if not etapas.exists():
        messages.error(request, "No hay etapas de inspeccion para esta orden!")


    orden = get_object_or_404(OrdenAlistamiento, id=orden_id)
    es_admin_mtto = request.user.groups.filter(name='Mtto_admin').exists()

    return render(request, "mantenimiento_app/detalle_orden.html", {"etapas": etapas, "orden": orden, "es_admin_mtto": es_admin_mtto})

@login_required
def generar_reporte_ordenes(request):
    # Obtiene los filtros de fecha
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    estado_id = request.GET.get('estado')

    # Consulta para filtrar las ordenes
    queryset = OrdenAlistamiento.objects.all()
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




@csrf_exempt
@permission_required('mantenimiento_app.change_ordenalistamiento', raise_exception=True)
def iniciar_orden(request, orden_id):
    """ Marca el inicio de la orden con la fecha y hora actual """
    if request.method == "POST":
        orden = get_object_or_404(OrdenAlistamiento, id=orden_id)
        estado_proceso = Estado.objects.get(nombre="En proceso")
        tecnico = orden.user

        # Valida si el tecnico tiene una orden abierta excepto la actual
        otra_orden = OrdenAlistamiento.objects.filter(
            user = tecnico,
            estado__nombre = "En proceso"
        ).exclude(id=orden_id).exists()

        if otra_orden:
            return JsonResponse({
                "success": False,
                "error": "Ya se encuentra una orden en proceso, debe finalizar antes de comenzar con una nueva orden"
            })

        if not orden.fecha_inicio:
            orden.fecha_inicio = now()
            orden.estado = estado_proceso 
            orden.save()

        return JsonResponse({
            "success": True,
            "fecha_inicio": orden.fecha_inicio.strftime("%Y-%m-%d %H:%M:%S")
        })
    

@csrf_exempt
@permission_required('mantenimiento_app.change_ordenalistamiento', raise_exception=True)
def iniciar_inspeccion_etapa(request, orden_id, etapa_nombre):
    """Inicia la inspección de la etapa especificada"""
    if request.method == "POST":
        orden = get_object_or_404(OrdenAlistamiento, id=orden_id)
        etapa_obj = get_object_or_404(Etapa, nombre=etapa_nombre)
        estado_proceso = get_object_or_404(Estado, nombre="En proceso")
        
        etapa_inspeccion = get_object_or_404(
            EtapaInspeccion, 
            orden=orden, 
            etapa=etapa_obj
        )
        
        if not etapa_inspeccion.fecha_inicio:
            etapa_inspeccion.fecha_inicio = now()
            etapa_inspeccion.estado = estado_proceso
            etapa_inspeccion.save()
        
        return JsonResponse({
            "success": True,
            "fecha_inicio": etapa_inspeccion.fecha_inicio.strftime("%Y-%m-%d %H:%M:%S"),
            "etapa": etapa_nombre
        })
    return JsonResponse({"success": False, "error": "Método no permitido"}, status=405)


@csrf_exempt
@permission_required('mantenimiento_app.change_ordenalistamiento', raise_exception=True)
def actualizar_observaciones(request):
    """ Actualiza las observaciones de una inspección """
    if request.method == "POST":
        data = json.loads(request.body)
        inspeccion = get_object_or_404(DetalleInspeccion, id=data["inspeccion_id"])
        inspeccion.observaciones = data["observaciones"]
        inspeccion.save()
        return JsonResponse({"success": True})


@csrf_exempt
@permission_required('mantenimiento_app.change_ordenalistamiento', raise_exception=True)
def finalizar_item(request, item_id):
    """ Marca la finalización del item con la fecha y hora actual """
    if request.method == "POST":
        item = get_object_or_404(DetalleInspeccion, id=item_id)
        estado_finalizado = Estado.objects.get(nombre="Finalizada")

        if not item.fecha_fin:
            item.fecha_fin = now()
            item.estado = estado_finalizado
            item.save()

        # Verificar si todos los items de la orden están finalizados
        items_etapa = DetalleInspeccion.objects.filter(orden_id=item.orden_id, etapa=item.etapa)
        if all(i.estado.nombre == "finalizada" for i in items_etapa):
            etapa = EtapaInspeccion.objects.get(
                orden_id = item.orden_id, etapa_id = item.etapa
            )
            etapa.estado = estado_finalizado
            etapa.save()


        return JsonResponse({
            "fecha_fin": item.fecha_fin.strftime("%Y-%m-%d %H:%M:%S"),
            "estado": item.estado.nombre
        })


# detalle orden mecanica
@login_required
@permission_required('mantenimiento_app.change_ordenalistamiento', raise_exception=True)
def trabajar_orden_mecanica(request, orden_id):
    inspecciones = DetalleInspeccion.objects.filter(orden_id= orden_id, etapa= 1)
    orden = get_object_or_404(OrdenAlistamiento, id=orden_id)

    es_admin_mtto = request.user.groups.filter(name='Mtto_admin').exists()
    
    return render(request, "mantenimiento_app/trabaja_orden.html", {"inspecciones": inspecciones, "orden": orden, "es_admin_mtto": es_admin_mtto})


# detalle orden externa
@login_required
@permission_required('mantenimiento_app.change_ordenalistamiento', raise_exception=True)
def trabajar_orden_externa(request, orden_id):
    inspecciones = DetalleInspeccion.objects.filter(orden_id= orden_id, etapa= 2)
    orden = get_object_or_404(OrdenAlistamiento, id=orden_id)

    es_admin_mtto = request.user.groups.filter(name='Mtto_admin').exists()
    return render(request, "mantenimiento_app/trabaja_orden.html", {"inspecciones": inspecciones, "orden": orden, "es_admin_mtto": es_admin_mtto})


# detalle orden interna
@login_required
@permission_required('mantenimiento_app.change_ordenalistamiento', raise_exception=True)
def trabajar_orden_interna(request, orden_id):
    inspecciones = DetalleInspeccion.objects.filter(orden_id= orden_id, etapa= 3)
    orden = get_object_or_404(OrdenAlistamiento, id=orden_id)

    es_admin_mtto = request.user.groups.filter(name='Mtto_admin').exists()
    return render(request, "mantenimiento_app/trabaja_orden.html", {"inspecciones": inspecciones, "orden": orden, "es_admin_mtto": es_admin_mtto})


# detalle orden electrica
@login_required
@permission_required('mantenimiento_app.change_ordenalistamiento', raise_exception=True)
def trabajar_orden_electrica(request, orden_id):
    inspecciones = DetalleInspeccion.objects.filter(orden_id= orden_id, etapa= 4)
    orden = get_object_or_404(OrdenAlistamiento, id=orden_id)

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


