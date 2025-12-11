from django.shortcuts import render, redirect
from .forms import *
from django.contrib import messages
from django.http import JsonResponse
from .utils import calcular_fecha_maxima_respuesta, obtener_festivos_colombia
from .models import Responsable



# Create your views here.
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
            'url': 'crear_radicados_enviados',
            'icono': 'fas fa-paper-plane',
            'grupos': ['todos']
        },
        {
            'nombre': 'Internos',
            'url': 'crear_radicados_internos',
            'icono': 'fas fa-building',
            'grupos': ['todos']
        },
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


def oficina_view(request):
    return render(request, 'radicacion_app/oficina.html')


def responsable_view(request):
    return render(request, 'radicacion_app/lista_responsables.html')


def entidades_view(request):
    return render(request, 'radicacion_app/lista_entidades.html')


def menu_radicados_recibidos_view(request):
    return render(request, 'radicacion_app/radicacion_menu_recibidos.html')


def radicados_recibidos_view(request):
    consecutivo_rec = ParametrosRadicacion.objects.get(pk=1)
    
    if request.method == 'POST':
        form = CrearRadicadoRecibidosForm(request.POST)
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
        form = CrearRadicadoRecibidosForm
            
    return render(request, 'radicacion_app/radicacion_recibidas.html', {'form': form})


def radicados_recibidos_pqrsd_view(request):


    return render(request, 'radicacion_app/radicacion_recibidas_pqrsd.html')


def radicados_enviados_view(request):
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


def radicados_internos_view(request):
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