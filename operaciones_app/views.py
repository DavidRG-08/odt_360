from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, logout, login as auth_login
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.contrib import messages
from datetime import datetime
from .forms import LoginViewForm, CrearSolicitudForm
from .models import *
from .reports import ReporterExcelRutas
from .forms import CustomUserCreationForm
from django.core.exceptions import PermissionDenied
from django.utils.timezone import now
from django.utils.dateparse import parse_date


# Vista para login de usuario
def login_view(request):    
    form = LoginViewForm()

    if request.method == 'POST':
        form = LoginViewForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username = username, password = password)
            print(f'Autenticando usuario: {username}, resultado: {user}') 
            
            if user is not None:
                auth_login(request, user)
                return redirect('home')
            else:
                form.add_error(None, 'usuario o clave incorrecta')
    
    return render(request, 'registration/login.html', {'form': form})


# Vista para salir de la aplicacion
def logout_view(request):
    logout(request)
    return redirect('login')

# vista para crear usuarios
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            #Guarda el usuario
            user = form.save()

            # Crea el perfil asociado
            Profile.objects.create(
                user = user,
                telefono = form.cleaned_data['telefono'],
                direccion = form.cleaned_data['direccion']
            )

            # Autenticar y redirigir
            # auth_login(request, user)

            return redirect('login')
        
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


# perfil
@login_required
@permission_required('operaciones_app.view_profile', raise_exception=True)
def profile(request, user_id):
    try:
        perfil = Profile.objects.get(user_id=user_id)
        user = perfil.user
        return render(request, "registration/profile.html", {"perfil": perfil, "user": user})
    except Profile.DoesNotExist:
        return render(request, "registration/no_profile.html", {"user_id": user_id})


# vista para crear operadores
@login_required
@permission_required('auth.add_user', raise_exception=True)
def crear_operador(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            #Guarda el usuario
            user = form.save()

            # Crea el perfil asociado
            Profile.objects.create(
                user = user,
                telefono = form.cleaned_data['telefono'],
                direccion = form.cleaned_data['direccion']
            )

            # Asignar el grupo "Operador" al usuario
            operador_group = Group.objects.get(name='Operador')
            user.groups.add(operador_group)

            # Autenticar y redirigir
            # auth_login(request, user)

            return redirect('operaciones')
        
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/create_operator.html', {'form': form})

# Ver lista de operadores
@login_required
@permission_required('auth.view_user', raise_exception=True)
def lista_operadores(request):
    # Obtener el grupo "operadores"
    operador_group = Group.objects.get(name='Operador')
    # filtrar los usuarios 
    operadores = User.objects.filter(groups=operador_group)
    # filtrar por nombre de usuario
    username = request.GET.get('operador')
    if username:
        operadores = operadores.filter(username__icontains=username)

    #Paginacion
    paginator = Paginator(operadores, 20)  # 20 usuarios por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "registration/lista_operadores.html", {"operador": page_obj.object_list, "page_obj": page_obj})

# detalle de cada operador
@login_required
@permission_required('auth.view_user', raise_exception=True)
def detalle_operador(request, id):
    operador = get_object_or_404(User, id=id)   
    if request.method == 'POST':
        operador.first_name = request.POST.get("first_name", operador.first_name)
        operador.last_name = request.POST.get("last_name", operador.last_name)
        operador.email = request.POST.get("email", operador.email)

        operador.profile.telefono = request.POST.get("phone", operador.profile.telefono)
        operador.profile.direccion = request.POST.get("address", operador.profile.direccion)

        operador.save()
        operador.profile.save()
        messages.success(request, "Datos actualizados correctamente.")
        return redirect("detalle_operador", id=operador.id)

    return render(request, "registration/detalle_operador.html", {"operador": operador})

    
# Pagina principal 
@login_required
def index(request):
    return render(request, 'index.html')

# pagina 403
@login_required
def custom_permission_denied_view(request, exception=None):
    context = {'mensaje': 'No tienes permisos para ver esta página.'}
    return render(request, '403.html', context, status=403)

# Modulo Operaciones 
@login_required 
def operaciones(request):
    return render(request, 'operaciones_app/operaciones.html')


# Vista para crear solicitud de ruta
@login_required
@permission_required('operaciones_app.add_solicitudruta', raise_exception=True)
def crear_solicitud(request):
    if request.method == 'POST':
        form = CrearSolicitudForm(request.POST)
        if form.is_valid():
            register = form.save(commit=False)
            register.operador = request.user
            register.usuario = request.user
            register.save()
            messages.success(request, "Solicitud creada con exito!!")

            return redirect('lista_solicitudes')
        
        else:
            print("Errores del formulario:", form.errors)
            messages.error(request, "Hubo un error al momento de crear la solicitud, por favor valide los datos ingresados o intente nuevamente!")
    
    else:
        form = CrearSolicitudForm
    
    return render(request, 'operaciones_app/crear_solicitud.html', {'form': form})


# Vista para consultar los registros creados por los operadores
@login_required
@permission_required('operaciones_app.view_solicitudruta', raise_exception=True)
def lista_solicitudes(request):
    registros = SolicitudRuta.objects.all().order_by('-fecha_solicitud')
    estado_ruta = EstadoRuta.objects.all()
    
    estado_id = request.GET.get('estado')
    if estado_id:
        registros = registros.filter(estado__id=estado_id)

    # filtrar segun el grupo de usuario
    if not request.user.groups.filter(name='Operaciones').exists() and not request.user.groups.filter(name='operaciones_view').exists():
        registros = registros.filter(usuario=request.user)
         
    # Rango de fechas
    start_date_op = request.GET.get('start_date_op')
    end_date_op = request.GET.get('end_date_op')

    # filtro en un rango de fechas
    if start_date_op and end_date_op:
        try:
            start_date_op = datetime.strptime(start_date_op, '%Y-%m-%d').date()
            end_date_op = datetime.strptime(end_date_op, '%Y-%m-%d').date()

            registros = registros.filter(
                fecha_solicitud__gte=start_date_op,
                fecha_solicitud__lte=end_date_op
            )
        except ValueError:
            pass
    
    paginator = Paginator(registros, 20)
    page_number = request.GET.get('page')
    page_obj_ope = paginator.get_page(page_number)

    grupo_operaciones = request.user.groups.filter(name='Operaciones').exists()
    grupo_view_operaciones = request.user.groups.filter(name='operaciones_view').exists()

    return render(request, 'operaciones_app/lista_solicitudes.html', {
        'page_obj_ope': page_obj_ope, 
        'estados': estado_ruta,
        'selected_estado': estado_id,
        'start_date_op': start_date_op,
        'end_date_op': end_date_op,
        'grupo_operaciones': grupo_operaciones,
        'grupo_view_operaciones': grupo_view_operaciones
        }
    )


# Obtiene los detalles de cada registro 
@login_required
@permission_required('operaciones_app.view_solicitudruta', raise_exception=True)
def obtener_detalles_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudRuta, id=solicitud_id)
    grupo_operaciones = request.user.groups.filter(name='Operaciones').exists()
    grupo_view_operaciones = request.user.groups.filter(name='operaciones_view').exists()

    return render(request, "operaciones_app/detalle_solicitud.html", {"solicitud": solicitud, "grupo_operaciones": grupo_operaciones, "grupo_view_operaciones": grupo_view_operaciones})


# Vista para crear cancelacion de ruta
@login_required
@permission_required('operaciones_app.add_solicitudruta', raise_exception=True)
def cancelar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudRuta, id=solicitud_id)
    nuevo_estado = EstadoRuta.objects.get(id=2)  # Estado "Cancelada"

    if request.method == 'POST':
        descripcion = request.POST.get("descripcion", "").strip()

        if not descripcion:
            messages.error(request, "debe ingresar una descripcion para la cancelacion")
            return redirect("detalle_solicitud", solicitud_id= solicitud_id)
        
        # Cambia estado de la solicitud
        solicitud.estado = nuevo_estado
        solicitud.save()

        # Guarda en la tabla de cancelaciones
        CancelacionRuta.objects.create(
            fecha_cancelacion = now(),
            operador = request.user.username,
            descripcion = descripcion,
            solicitud = solicitud
        )

        messages.success(request, "la ruta ha sido cancelada exitosamente")



        return redirect('lista_solicitudes') # Redirige al listado de solicitudes


@login_required
def generate_report_rutas(request):
    # Obtener los filtros de fecha
    start_date_op = request.GET.get('start_date_op')
    end_date_op = request.GET.get('end_date_op')
    estado_id = request.GET.get('estado')
    
    # Consulta para filtrar los registros
    queryset = SolicitudRuta.objects.all()

    if start_date_op and end_date_op:
        queryset = queryset.filter(
            fecha_solicitud__date__gte=parse_date(start_date_op),
            fecha_solicitud__date__lte=parse_date(end_date_op)
        )
    
    try:
        if estado_id:
            queryset = queryset.filter(estado_id=estado_id)
    except ValueError:
        pass

    # Generar el reporte solo con los registros filtrados
    report = ReporterExcelRutas(queryset)
    return report.get(request)
