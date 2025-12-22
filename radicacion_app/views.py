from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from django.contrib import messages
from django.http import JsonResponse
from .utils import calcular_fecha_maxima_respuesta, obtener_festivos_colombia
from .models import Responsable
from django.core.paginator import Paginator
from datetime import datetime
from django.contrib.auth.decorators import login_required, permission_required


@login_required
def radicacion(request):
    MODULOS_RADICACION = [
        {
            'nombre': 'Recibidos',
            'url': 'radicados_recibidos',
            'icono': 'fas fa-envelope-open-text',
            'grupos': ['todos']
        },
        {
            'nombre': 'Enviados',
            'url': 'radicados_enviados',
            'icono': 'fas fa-paper-plane',
            'grupos': ['todos']
        },
        {
            'nombre': 'Internos',
            'url': 'radicados_internos',
            'icono': 'fas fa-building',
            'grupos': ['todos']
        },
        {
            'nombre': 'Propiedades',
            'url': 'propiedades',
            'icono': 'fas fa-folder-open',
            'grupos': ['admin', 'radicacion']
        }
    ]
    return render(request, 'radicacion_app/radicacion.html', {'modulos': MODULOS_RADICACION})


def get_festivos_colombia(request):
    """
    API que retorna los festivos de Colombia del año actual.
    Usado por JavaScript para validaciones.
    """
    festivos = obtener_festivos_colombia()
    return JsonResponse({'festivos': festivos})


def calcular_fecha_respuesta(request):
    """
    API que calcula la fecha máxima de respuesta.
    
    GET params:
        dias: número de días hábiles a sumar
    """
    if request.method == 'GET':
        try:
            dias = int(request.GET.get('dias', 0))
            
            if dias < 0:
                return JsonResponse({'error': 'Los días no pueden ser negativos'}, status=400)
            
            fecha_maxima = calcular_fecha_maxima_respuesta(dias)
            
            return JsonResponse({
                'fecha_maxima': fecha_maxima.strftime('%Y-%m-%d'),
                'dias_sumados': dias,
                'exito': True
            })
        
        except ValueError:
            return JsonResponse({'error': 'Número de días inválido'}, status=400)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


def get_oficina_responsable(request):
    """
    API que retorna la oficina de un responsable.
    
    GET params:
        responsable_id: ID del responsable
    """
    if request.method == 'GET':
        try:
            responsable_id = request.GET.get('responsable_id')
            
            if not responsable_id:
                return JsonResponse({'error': 'ID de responsable requerido'}, status=400)
            
            responsable = Responsable.objects.get(id=responsable_id)
            
            return JsonResponse({
                'exito': True,
                'oficina_id': responsable.oficina.id,
                'oficina_nombre': responsable.oficina.nombre
            })
        
        except Responsable.DoesNotExist:
            return JsonResponse({'error': 'Responsable no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


# Vistas propias de la aplicacion

@login_required
@permission_required('radicacion_app.view_oficina', raise_exception=True)
def view_oficina(request):
    oficinas = Oficina.objects.all().order_by('id')

    # Filtro por nombre de oficina
    nombre_oficina = request.GET.get('nombre_oficina')
    if nombre_oficina:
        oficinas = oficinas.filter(nombre__icontains=nombre_oficina)

    # Paginacion
    paginator = Paginator(oficinas, 20)
    page_number = request.GET.get('page')
    page_obj_oficina = paginator.get_page(page_number)

    return render(request, 'radicacion_app/lista_oficinas.html', {
        'page_obj_oficina': page_obj_oficina,
        'nombre_oficina': nombre_oficina,
    })


@permission_required('radicacion_app.add_oficina', raise_exception=True)
@login_required
def crear_oficina(request):
    if request.method == 'POST':
        form = CrearOficinaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Oficina creada exitosamente.')
            return redirect('lista_oficinas')
        else:
            messages.error(request, 'Error al crear la oficina. Por favor verifica los datos ingresados.')
    else:
        form = CrearOficinaForm()

    return render(request, 'radicacion_app/crear_oficina.html', {'form': form})


@permission_required('radicacion_app.view_responsable', raise_exception=True)
@login_required
def view_responsable(request):
    responsables = Responsable.objects.all().order_by('id')

    nombre_responsable = request.GET.get('nombre_responsable')
    if nombre_responsable:
        responsables = responsables.filter(nombre__icontains=nombre_responsable)

    # Paginacion
    paginator = Paginator(responsables, 20)
    page_number = request.GET.get('page')
    page_obj_responsable = paginator.get_page(page_number)                                                                                                                                                                                                                                          

    return render(request, 'radicacion_app/lista_responsables.html', {
        'page_obj_responsable': page_obj_responsable,
        'nombre_responsable': nombre_responsable,
    })


@permission_required('radicacion_app.add_responsable', raise_exception=True)
@login_required
def crear_responsable(request):
    if request.method == 'POST':
        form = CrearResponsableForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Responsable creado exitosamente.')
            return redirect('lista_responsables')
        else:
            messages.error(request, 'Error al crear el responsable. Por favor verifica los datos ingresados.')
    else:
        form = CrearResponsableForm()

    return render(request, 'radicacion_app/crear_responsable.html', {'form': form})



@login_required
@permission_required('radicacion_app.view_entidad', raise_exception=True)
def view_entidades(request):
    entidades = Entidad.objects.all().order_by('id')

    nombre_entidad = request.GET.get('nombre_entidad')
    if nombre_entidad:
        entidades = entidades.filter(nombre__icontains=nombre_entidad)

    # Paginacion
    paginator = Paginator(entidades, 20)
    page_number = request.GET.get('page')
    page_obj_entidad = paginator.get_page(page_number)
    
    return render(request, 'radicacion_app/lista_entidades.html', {
        'page_obj_entidad': page_obj_entidad,
        'nombre_entidad': nombre_entidad,
    })


@login_required
@permission_required('radicacion_app.add_entidad', raise_exception=True)
def crear_entidad(request):
    if request.method == 'POST':
        form = CrearEntidadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entidad creada exitosamente.')
            return redirect('lista_entidades')
        else:
            messages.error(request, 'Error al crear la entidad. Por favor verifica los datos ingresados.')
    else:
        form = CrearEntidadForm()

    return render(request, 'radicacion_app/crear_entidad.html', {'form': form})


@login_required
@permission_required('radicacion_app.view_entidad', raise_exception=True)
def view_tipo_documento(request):
    documento = TipoDocumento.objects.all().order_by('id')

    tipo_documento = request.GET.get('tipo_documento')
    if tipo_documento:
        documento = documento.filter(tipo__icontains=tipo_documento)

    # Paginacion
    paginator = Paginator(documento, 20)
    page_number = request.GET.get('page')
    page_obj_documento = paginator.get_page(page_number)

    return render(request, 'radicacion_app/lista_documentos.html', {
        'page_obj_documento': page_obj_documento,
        'tipo_documento': tipo_documento,
    })


@login_required
@permission_required('radicacion_app.add_entidad', raise_exception=True)
def crear_tipo_documento(request):
    if request.method == 'POST':
        form = CrearTipoDocumentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de documento creado exitosamente.')
            return redirect('lista_tipo_documentos')
        else:
            messages.error(request, 'Error al crear el tipo de documento. Por favor verifica los datos ingresados.')
    else:
        form = CrearTipoDocumentoForm()

    return render(request, 'radicacion_app/crear_tipo_documento.html', {'form': form})


# VIstas para los menus de radicacion
@login_required
def menu_propiedades(request):
    return render(request, 'radicacion_app/propiedades.html')


@login_required
def menu_radicados_recibidos(request):
    return render(request, 'radicacion_app/radicacion_menu_recibidos.html')

@login_required
def menu_radicados_enviados(request):
    return render(request, 'radicacion_app/radicacion_menu_enviados.html')

@login_required
def menu_radicados_internos(request):
    return render(request, 'radicacion_app/radicacion_menu_internos.html')

# funciones para crear los diferentes tipos de radicados

# Radicados Recibidos
@login_required
@permission_required('radicacion_app.add_radicacionrecibidos', raise_exception=True)
def crear_radicados_recibidos(request):
    consecutivo_rec = ParametrosRadicacion.objects.get(pk=1)
    
    if request.method == 'POST':
        form = CrearRadicadoRecibidosForm(request.POST)
        if form.is_valid():
            radicado = form.save(commit=False)
           
            radicado.id = consecutivo_rec.generar_id_radicado()
            radicado.radicador = request.user
            radicado.save()

            messages.success(request, 'Radicado creado exitosamente.')
            return redirect('lista_radicados_recibidos')
        
        else:
            messages.error(request, 'Error al crear el radicado. Por favor verifica los datos ingresados.')
    
    else:
        form = CrearRadicadoRecibidosForm
            
    return render(request, 'radicacion_app/radicacion_recibidas.html', {'form': form})


@login_required
@permission_required('radicacion_app.view_radicacionrecibidos', raise_exception=True)
def view_radicados_recibidos(request):
    radicados_recibidos = RadicacionRecibidos.objects.all().order_by('-id')
    oficinas = Oficina.objects.all()

    # Filtrar por oficina
    oficina_id = request.GET.get('oficina')
    if oficina_id:
        radicados_recibidos = radicados_recibidos.filter(oficina__id=oficina_id)


    #rango de fechas
    start_date_rad = request.GET.get('start_date_rad')
    end_date_rad = request.GET.get('end_date_rad')

    if start_date_rad and end_date_rad:
        try:
            start_date_rad = datetime.strptime(start_date_rad, '%Y-%m-%d').date()
            end_date_rad = datetime.strptime(end_date_rad, '%Y-%m-%d').date()

            radicados_recibidos = radicados_recibidos.filter(
                fecha_radicacion__gte=start_date_rad,
                fecha_radicacion__lte=end_date_rad
            )
        except ValueError:
            pass

    # Paginación
    paginator = Paginator(radicados_recibidos, 20)  # 10 radicados por página
    page_number = request.GET.get('page')
    page_obj_recibidos = paginator.get_page(page_number)

    return render(request, 'radicacion_app/lista_radicados_recibidos.html', {
        'page_obj_recibidos': page_obj_recibidos,
        'start_date_rad': start_date_rad,
        'end_date_rad': end_date_rad,
        'oficinas': oficinas,
        'selected_oficina': oficina_id,
    })


@login_required
def editar_radicado_recibido(request, radicado_id):
    instancia = get_object_or_404(RadicacionRecibidos, pk=radicado_id)
    if request.method == 'POST':
        form = UpdateRadicadosRecibidosForm(request.POST, instance=instancia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Radicado actualizado exitosamente.')
            return redirect('lista_radicados_recibidos')
    
    else:
        form = UpdateRadicadosRecibidosForm(instance=instancia)

    return render(request, 'radicacion_app/editar_radicado_recibido.html', {'form': form, 'instancia': instancia})


@login_required
def obtener_detalle_rad_recibido(request, radicado_id):
    rad_recibido = RadicacionRecibidos.objects.get(id=radicado_id)

    return render(request, 'radicacion_app/detalle_radicado_recibidos.html', {"radicado_recibido": rad_recibido})



# Radicados Recibidos PQRSD

def radicados_recibidos_pqrsd_view(request):


    return render(request, 'radicacion_app/radicacion_recibidas_pqrsd.html')



# Radicados Enviados
@login_required
@permission_required('radicacion_app.add_radicacionenviados', raise_exception=True)
def crear_radicados_enviados(request):
    consecutivo_env = ParametrosRadicacion.objects.get(pk=2)

    if request.method == 'POST':
        form = CrearRadicadoEnviadosForm(request.POST)
        if form.is_valid():
            recibido = form.save(commit=False)

            recibido.id = consecutivo_env.generar_id_radicado()
            recibido.radicador = request.user
            recibido.save()

            messages.success(request, 'Radicado enviado creado exitosamente.')
            return redirect('home')
        
        else:
            messages.error(request, 'Error al crear el radicado enviado. Por favor verifica los datos ingresados.')
    
    else:
        form = CrearRadicadoEnviadosForm()
    
    return render(request, 'radicacion_app/radicacion_enviadas.html', {'form': form})


@login_required
@permission_required('radicacion_app.view_radicacionenviados', raise_exception=True)
def view_radicados_enviados(request):
    radicados_enviados = RadicacionEnviados.objects.all().order_by('-id')
    oficinas = Oficina.objects.all()

    # Filtrar por oficina
    oficina_id = request.GET.get('oficina')
    if oficina_id:
        radicados_enviados = radicados_enviados.filter(oficina__id=oficina_id)


    #rango de fechas
    start_date_rad = request.GET.get('start_date_rad')
    end_date_rad = request.GET.get('end_date_rad')

    if start_date_rad and end_date_rad:
        try:
            start_date_rad = datetime.strptime(start_date_rad, '%Y-%m-%d').date()
            end_date_rad = datetime.strptime(end_date_rad, '%Y-%m-%d').date()

            radicados_enviados = radicados_enviados.filter(
                fecha_radicacion__gte=start_date_rad,
                fecha_radicacion__lte=end_date_rad
            )
        except ValueError:
            pass

    # Paginación
    paginator = Paginator(radicados_enviados, 20)  # 10 radicados por página
    page_number = request.GET.get('page')
    page_obj_enviados = paginator.get_page(page_number)

    return render(request, 'radicacion_app/lista_radicados_enviados.html', {
        'page_obj_enviados': page_obj_enviados,
        'start_date_rad': start_date_rad,
        'end_date_rad': end_date_rad,
        'oficinas': oficinas,
        'selected_oficina': oficina_id,
    })


@login_required
def obtener_detalle_rad_enviado(request, radicado_id):
    rad_enviado = RadicacionEnviados.objects.get(id=radicado_id)

    return render(request, 'radicacion_app/detalle_radicado_enviados.html', {"radicado_enviado": rad_enviado})



# Radicados Internos
@login_required
@permission_required('radicacion_app.add_radicacioninternos', raise_exception=True)
def crear_radicados_internos(request):
    consecutivo_rec = ParametrosRadicacion.objects.get(pk=3)
    
    if request.method == 'POST':
        form = CrearRadicadoInternosForm(request.POST)
        if form.is_valid():
            radicado = form.save(commit=False)
           
            radicado.id = consecutivo_rec.generar_id_radicado()
            radicado.radicador = request.user
            radicado.save()

            messages.success(request, 'Radicado creado exitosamente.')
            return redirect('home')
        
        else:
            messages.error(request, 'Error al crear el radicado. Por favor verifica los datos ingresados.')
    
    else:
        form = CrearRadicadoInternosForm()
            
    return render(request, 'radicacion_app/radicacion_internas.html', {'form': form})


@login_required
@permission_required('radicacion_app.view_radicacioninternos', raise_exception=True)
def view_radicados_internos(request):
    radicados_internos = RadicacionInternos.objects.all().order_by('-id')
    oficinas = Oficina.objects.all()

    # Filtrar por oficina
    oficina_id = request.GET.get('oficina')
    if oficina_id:
        radicados_internos = radicados_internos.filter(oficina__id=oficina_id)


    #rango de fechas
    start_date_rad = request.GET.get('start_date_rad')
    end_date_rad = request.GET.get('end_date_rad')

    if start_date_rad and end_date_rad:
        try:
            start_date_rad = datetime.strptime(start_date_rad, '%Y-%m-%d').date()
            end_date_rad = datetime.strptime(end_date_rad, '%Y-%m-%d').date()

            radicados_internos = radicados_internos.filter(
                fecha_radicacion__gte=start_date_rad,
                fecha_radicacion__lte=end_date_rad
            )
        except ValueError:
            pass

    # Paginación
    paginator = Paginator(radicados_internos, 20)  # 20 radicados por página
    page_number = request.GET.get('page')
    page_obj_internos = paginator.get_page(page_number)

    return render(request, 'radicacion_app/lista_radicados_internos.html', {
        'page_obj_internos': page_obj_internos,
        'start_date_rad': start_date_rad,
        'end_date_rad': end_date_rad,
        'oficinas': oficinas,
        'selected_oficina': oficina_id,
    })


@login_required
def obtener_detalle_rad_interno(request, radicado_id):
    rad_interno = RadicacionInternos.objects.get(id=radicado_id)

    return render(request, 'radicacion_app/detalle_radicado_interno.html', {"radicado_interno": rad_interno})