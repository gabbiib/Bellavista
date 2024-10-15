from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from .models import Usuarios, Tareas, Reportes_Problemas, Asignacion, Rol
from django.contrib.auth.views import LogoutView
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from twilio.rest import Client
from .forms import ReporteForm
from .tokens import account_activation_token
from django.urls import reverse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .forms import RecuperarContrasenaForm, ContactarAdminForm
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.db.models import Q, Count, Value
from django.views.decorators.http import require_POST
from django.db.utils import IntegrityError
from django.db.models.functions import Concat
from datetime import datetime
import random
import string
from django.db.models import Count, Avg, F
from django.db.models.functions import TruncMonth
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string



# Create your views here.
def inicio(request):
    return render(request, 'inicio.html')

def reporte(request):
    return render(request, 'reporte.html')

def reporte_view(request):
    trabajadores = Usuarios.objects.filter(rol__id_rol=2)

    if request.method == 'POST':
        rut_usuario = request.POST.get('rut_usuario')
        tipo_incidente = request.POST.get('tipo_incidente')
        descripcion = request.POST.get('descripcion')
        marco = request.POST.get('marco')
        medida_marco = request.POST.get('medida')
        foto_url = request.FILES.get('foto')
        latitud = request.POST.get('latitud')
        longitud = request.POST.get('longitud')

        try:
            usuario = Usuarios.objects.get(rut=rut_usuario)
            
            nuevo_reporte = Reportes_Problemas(
                rut_usuario=usuario,
                tipo_incidente=tipo_incidente,
                descripcion=descripcion,
                marco=marco,
                medida_marco=medida_marco,
                foto_url=foto_url,
                fecha_reporte=timezone.now(),
                latitud=latitud,
                longitud=longitud
            )
            nuevo_reporte.save()

            administradores = Usuarios.objects.filter(rol__id_rol=1)

            mensaje = (
                f'El usuario {usuario.nombre} {usuario.apellido_p} {usuario.apellido_m} '
                f'ha reportado un problema.\nDescripción: {descripcion}\nMarco: {marco}\nFecha: {nuevo_reporte.fecha_reporte.strftime("%Y-%m-%d %H:%M:%S")}'
            )

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            for admin in administradores:
                client.messages.create(
                    body=mensaje,
                    from_='whatsapp:' + settings.TWILIO_PHONE_NUMBER,
                    to='whatsapp:' + admin.telefono
                )

            return redirect('reporte_exito') 

        except Usuarios.DoesNotExist:
            return render(request, 'reporte.html', {'trabajadores': trabajadores, 'error': 'Usuario no encontrado.'})

    return render(request, 'reporte.html', {'trabajadores': trabajadores})

    
def logout_view(request):
    response = LogoutView.as_view()(request)
    return response

@login_required
def trabajador(request):
    rut_usuario = request.user.rut

    # Filtra las asignaciones usando el campo correcto
    asignaciones = Asignacion.objects.filter(trabajador__rut=rut_usuario).exclude(estado='terminada')

    # Inicializa una lista para las tareas asignadas
    tareas_asignadas = []
    for asignacion in asignaciones:
        tareas_asignadas.append({
            'id': asignacion.tarea.id,
            'descripcion': asignacion.tarea.descripcion,
            'prioridad': asignacion.tarea.prioridad,
            'fecha_asignacion': asignacion.asignado_en,
            'estado': asignacion.estado,
        })

    context = {
        'tareas_asignadas': tareas_asignadas,
    }

    return render(request, 'trabajador.html', context)

@login_required
def editar_perfil(request):
    usuario = Usuarios.objects.get(rut=request.user.rut)

    telefono_cambiado = False
    contrasena_cambiada = False

    if request.method == 'POST':
        nuevo_telefono = request.POST.get('telefono')
        nueva_contrasena = request.POST.get('contrasena')

        if nuevo_telefono and nuevo_telefono != usuario.telefono:
            usuario.telefono = f'+569{nuevo_telefono}'
            telefono_cambiado = True

        if nueva_contrasena:
            usuario.contrasena = make_password(nueva_contrasena)
            contrasena_cambiada = True

        usuario.save()

        if telefono_cambiado and contrasena_cambiada:
            messages.success(request, 'Tu telefono y contraseña han sido actualizados.')
        elif telefono_cambiado:
            messages.success(request, 'Tu telefono ha sido actualizado.')
        elif contrasena_cambiada:
            messages.success(request, 'Tu contraseña ha sido actualizada.')
        else:
            messages.info(request, 'No se realizaron cambios.')

        return redirect('editar_perfil')

    contexto = {'telefono_actual': usuario.telefono}
    return render(request, 'editar_perfil.html', contexto)


def recuperar_contrasena(request):
    return render(request, 'recuperar_contrasena.html')

def reporte_exito(request):
    return render(request, 'reporte_exito.html')

def contacto(request):
    if request.method == 'POST':
        nombre = request.POST.get('name')
        telefono = request.POST.get('phone')
        email = request.POST.get('email')
        mensaje = request.POST.get('message')

        mensaje_correo = f"Nombre: {nombre}\nTeléfono: {telefono}\nEmail: {email}\n\nMensaje:\n{mensaje}"

        try:
            send_mail(
                'Nuevo mensaje de contacto',  
                mensaje_correo,               
                email,                        
                [settings.DEFAULT_FROM_EMAIL], 
            )
            messages.success(request, 'Su mensaje ha sido enviado con éxito.')
        except Exception as e:
            messages.error(request, f'Hubo un error al enviar el mensaje: {e}')

    return render(request, 'contacto.html')

def nosotros(request):
    return render(request, 'nosotros.html')


def login_view(request):
    if request.method == 'POST':
        rut = request.POST['rut']
        password = request.POST['password']
        remember_me = request.POST.get('remember_me')

        try:
            usuario = Usuarios.objects.get(rut=rut)
            
            if check_password(password, usuario.password):
                user = authenticate(request, username=rut, password=password)
                
                if user is not None:
                    login(request, user)  
                    
                    if request.user.is_authenticated:
                        print("Usuario autenticado:", request.user.rut) 

                    if not remember_me: 
                        request.session.set_expiry(0)  
                    else:
                        request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                    
                    if usuario.rol.id_rol == 2:
                        return redirect('trabajador')  
                    elif usuario.rol.id_rol == 1:
                        return redirect('administrador')  
                    else:
                        return render(request, 'registration/login.html', {'error': 'Rol de usuario no reconocido.'})
                else:
                    return render(request, 'registration/login.html', {'error': 'Error en la autenticación.'})
            else:
                return render(request, 'registration/login.html', {'error': 'Contraseña incorrecta.'})
        except Usuarios.DoesNotExist:
            return render(request, 'registration/login.html', {'error': 'El RUT ingresado no existe.'})

    return render(request, 'registration/login.html')


def administrador(request):
    return render(request, 'administrador.html')

def generar_codigo():
    return get_random_string(length=6, allowed_chars=string.ascii_letters + string.digits)


def enviar_enlace_view(request):
    if request.method == 'POST':
        rut = request.POST.get('rut')
        try:
            usuario = Usuarios.objects.get(rut=rut)
            codigo_recuperacion = generar_codigo()
            
            usuario.codigo_recuperacion = codigo_recuperacion
            usuario.save()
            
            enlace_recuperacion = request.build_absolute_uri(
                reverse('recuperar_contrasena_codigo', args=[codigo_recuperacion])
            )
            
            mensaje = f"Hola {usuario.nombre},\n\nAquí está el enlace para recuperar tu contraseña: {enlace_recuperacion}\n\nEste enlace es válido por 1 hora."

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            
            client.messages.create(
                body=mensaje,
                from_='whatsapp:' + settings.TWILIO_PHONE_NUMBER,  
                to='whatsapp:' + usuario.telefono  
            )

            messages.success(request, 'Hemos enviado un enlace para recuperar tu contraseña a tu WhatsApp.')
            return redirect('recuperar_contrasena')  
            
        except Usuarios.DoesNotExist:
            messages.error(request, 'El RUT proporcionado no está asociado a ninguna cuenta.')
            return redirect('recuperar_contrasena')  
            
    return render(request, 'recuperar_contrasena.html')

def recuperar_contrasena_codigo(request, codigo):
    if request.method == 'POST':
        nueva_contrasena = request.POST.get('nueva_contrasena')
        try:
            usuario = get_object_or_404(Usuarios, codigo_recuperacion=codigo)

            usuario.contrasena = make_password(nueva_contrasena)
            usuario.codigo_recuperacion = None  
            usuario.save()

            messages.success(request, 'Tu contraseña ha sido actualizada exitosamente.')
            return redirect('login')
        except Usuarios.DoesNotExist:
            messages.error(request, 'Código de recuperación inválido.')
    return render(request, 'recuperar_contrasena_codigo.html')

def contactar_admin_view(request):
    if request.method == 'POST':
        rut = request.POST.get('rut')
        try:
            usuario = Usuarios.objects.get(rut=rut)
            nombre = usuario.nombre
            apellido_p = usuario.apellido_p
            apellido_m = usuario.apellido_m
            mensaje = (
                f'El usuario {nombre} {apellido_p} {apellido_m} con el RUT {rut} ha olvidado su contraseña.'
            )
            send_mail(
                'Solicitud de Recuperación de Contraseña',
                mensaje,
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
            messages.success(request, 'Hemos enviado un correo al administrador.')
        except Usuarios.DoesNotExist:
            messages.error(request, 'El RUT proporcionado no está asociado a ninguna cuenta.')
        return redirect('recuperar_contrasena')
    return render(request, 'recuperar_contrasena.html')

def ver_reportes(request):
    ordenar = request.GET.get('ordenar', 'asc')
    
    if ordenar == 'asc':
        reportes = Reportes_Problemas.objects.all().order_by('fecha_reporte')
    else:
        reportes = Reportes_Problemas.objects.all().order_by('-fecha_reporte')
    
    context = {
        'reportes': reportes
    }
    return render(request, 'ver_reportes.html', context)

def ver_imagen(request, reporte_id):
    reporte = get_object_or_404(Reportes_Problemas, id=reporte_id)
    return render(request, 'ver_imagen.html', {'reporte': reporte})

def actualizar_tarea(request, tarea_id):
    tarea = Asignacion.objects.get(tarea_id=tarea_id)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        tarea.estado = nuevo_estado
        tarea.save()  
        return redirect('trabajador') 
    
    return render(request, 'actualizar_tarea.html', {'tarea': tarea})

def editar_reporte(request, id):
    reporte = get_object_or_404(Reportes_Problemas, id=id)

    if request.method == 'POST':
        form = ReporteForm(request.POST, instance=reporte)
        if form.is_valid():
            form.save() 
            messages.success(request, "El reporte fue actualizado exitosamente.")
            return redirect('ver_reportes')  
        else:
            print(form.errors)  

    else:
        form = ReporteForm(instance=reporte)  
    
    return render(request, 'editar_reporte.html', {'form': form, 'reporte': reporte})

    ##benja
def lista_tareas(request):
    tareas_asignadas_ids = Asignacion.objects.values_list('tarea_id', flat=True)
    tareas = Tareas.objects.exclude(id__in=tareas_asignadas_ids)  # Excluir tareas asignadas
    trabajadores = Usuarios.objects.filter(rol__nombre='Trabajador')  # Solo trabajadores
    asignaciones = Asignacion.objects.all()

    return render(request, 'lista_tareas.html', {
        'tareas': tareas,
        'trabajadores': trabajadores,
        'asignaciones': asignaciones,
    })

def asignar_tarea_ajax(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        tarea_id = request.POST.get('tarea_id')
        trabajador_id = request.POST.get('trabajador_id')

        # Verifica que ambos IDs existan
        if not tarea_id or not trabajador_id:
            return JsonResponse({'error': 'Faltan datos de la tarea o trabajador.'}, status=400)

        # Busca los objetos de Tarea y Trabajador (Usuario con rol de Trabajador)
        try:
            tarea = Tareas.objects.get(id=tarea_id)
            trabajador = Usuarios.objects.get(rut=trabajador_id, rol__nombre='Usuario')

            # Crear la asignación
            asignacion = Asignacion.objects.create(tarea=tarea, trabajador=trabajador, estado='En espera')
            return JsonResponse({
                'message': 'Asignación realizada correctamente.',
                'asignacion_id': asignacion.id,
                'tarea_nombre': tarea.nombre,
                'desc': tarea.descripcion,
                'prioridad': tarea.prioridad,
                'trabajador_nombre': trabajador.full_name(),
                'estado': asignacion.estado,
            })
        except Tareas.DoesNotExist:
            return JsonResponse({'error': 'La tarea no existe.'}, status=404)
        except Usuarios.DoesNotExist:
            return JsonResponse({'error': 'El trabajador no existe o no tiene el rol adecuado.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Solicitud no válida.'}, status=400)

def eliminar_asignacion_ajax(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        asignacion_id = request.POST.get('asignacion_id')

        try:
            asignacion = Asignacion.objects.get(id=asignacion_id)
            tarea = asignacion.tarea
            asignacion.delete()

            trabajadores = Usuarios.objects.filter(rol__nombre='Trabajador')
            trabajadores_data = [{'id': trabajador.rut, 'nombre': trabajador.full_name()} for trabajador in trabajadores]

            # Devuelve los datos de la tarea eliminada y los trabajadores
            return JsonResponse({
                'message': 'Asignación eliminada correctamente.',
                'tarea_id': tarea.id,
                'tarea_nombre': tarea.nombre,
                'desc': tarea.descripcion,
                'prioridad': tarea.prioridad,
                'trabajadores': trabajadores_data
            })
        except Asignacion.DoesNotExist:
            return JsonResponse({'error': 'La asignación no existe.'}, status=404)
    return JsonResponse({'error': 'Solicitud no válida.'}, status=400)

def editar_asignacion_ajax(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        asignacion_id = request.POST.get('asignacion_id')
        trabajador_id = request.POST.get('trabajador_id')
        estado = request.POST.get('estado')

        try:
            asignacion = Asignacion.objects.get(id=asignacion_id)
            trabajador = Usuarios.objects.get(rut=trabajador_id, rol__nombre='Trabajador')
            
            # Actualizar la asignación
            asignacion.trabajador = trabajador
            asignacion.estado = estado
            asignacion.save()

            return JsonResponse({
                'message': 'Asignación actualizada correctamente.',
                'asignacion_id': asignacion.id,
                'tarea_nombre': asignacion.tarea.nombre,
                'desc': asignacion.tarea.descripcion,
                'prioridad': asignacion.tarea.prioridad,
                'trabajador_nombre': trabajador.full_name(),
                'trabajador_id': trabajador_id,
                'estado': asignacion.estado,
            })
        except Asignacion.DoesNotExist:
            return JsonResponse({'error': 'La asignación no existe.'}, status=404)
        except Usuarios.DoesNotExist:
            return JsonResponse({'error': 'El trabajador no existe.'}, status=404)
    return JsonResponse({'error': 'Solicitud no válida.'}, status=400)

def eliminar_tarea_ajax(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        tarea_id = request.POST.get('tarea_id')

        try:
            tarea = Tareas.objects.get(id=tarea_id)
            tarea.delete()

            return JsonResponse({
                'message': 'Tarea eliminada correctamente.',
                'tarea_id': tarea_id,
            })
        except Tareas.DoesNotExist:
            return JsonResponse({'error': 'La tarea no existe.'}, status=404)
    return JsonResponse({'error': 'Solicitud no válida.'}, status=400)

def editar_tarea_ajax(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        tarea_id = request.POST.get('tarea_id')
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        prioridad = request.POST.get('prioridad')

        try:
            tarea = Tareas.objects.get(id=tarea_id)
            tarea.nombre = nombre
            tarea.descripcion = descripcion
            tarea.prioridad = prioridad
            tarea.save()

            trabajadores = Usuarios.objects.filter(rol__nombre='Trabajador')
            trabajadores_data = [{'id': trabajador.rut, 'nombre': trabajador.full_name()} for trabajador in trabajadores]

            return JsonResponse({
                'message': 'Tarea actualizada correctamente.',
                'tarea_id': tarea_id,
                'nombre': tarea.nombre,
                'descripcion': tarea.descripcion,
                'prioridad': tarea.prioridad,
                'trabajadores': trabajadores_data,  # Enviar la lista de trabajadores
            })
        except Tareas.DoesNotExist:
            return JsonResponse({'error': 'La tarea no existe.'}, status=404)
    return JsonResponse({'error': 'Solicitud no válida.'}, status=400)

def crear_tarea_ajax(request):
    print("Llamada a crear_tarea_ajax")
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        prioridad = request.POST.get('prioridad')
        

        if not nombre or not prioridad or not descripcion:
            return JsonResponse({'error': 'Faltan datos obligatorios.'}, status=400)

        tarea = Tareas.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            prioridad=prioridad,
        )

        # Recargar la lista de tareas
        tareas_asignadas_ids = Asignacion.objects.values_list('tarea_id', flat=True)
        tareas = Tareas.objects.exclude(id__in=tareas_asignadas_ids)
        html = render_to_string('partials/tabla_tareas.html', {'tareas': tareas})

        return JsonResponse({'message': 'Tarea creada correctamente.', 'html': html})
    return JsonResponse({'error': 'Solicitud no válida.'}, status=400)

def filtrar_tareas_ajax(request):
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        filter_name = request.GET.get('filterName', '')
        filter_priority = request.GET.get('filterPriority', '')
        filter_date = request.GET.get('filterDate', '')
        filter_state = request.GET.get('filterState', '')
        filter_worker = request.GET.get('filterWorker', '')
        hide_completed = request.GET.get('hideCompleted', 'off') == 'on'

        # Filtrar tareas no asignadas
        tareas_asignadas_ids = Asignacion.objects.values_list('tarea_id', flat=True)
        tareas = Tareas.objects.exclude(id__in=tareas_asignadas_ids)
                
        print("hide_completed:", hide_completed)
        print("filter_state:", filter_state)

        if filter_name:
            tareas = tareas.filter(nombre__icontains=filter_name)
        if filter_priority:
            tareas = tareas.filter(prioridad=filter_priority)


        # Filtrar tareas asignadas
        asignaciones = Asignacion.objects.all()
        for asignacion in asignaciones:
            print("Estado de la tarea", asignacion.tarea.nombre, ":", asignacion.estado)

        # Filtrado del estado de la asignación
        if hide_completed:
            asignaciones = asignaciones.filter(estado__in=['En espera', 'En progreso'])
        if filter_state:
            asignaciones = asignaciones.filter(estado__in=[filter_state])



        if filter_name:
            asignaciones = asignaciones.filter(tarea__nombre__icontains=filter_name)
        if filter_priority:
            asignaciones = asignaciones.filter(tarea__prioridad=filter_priority)
        if filter_worker:
            asignaciones = asignaciones.filter(trabajador__rut=filter_worker)

        trabajadores = Usuarios.objects.filter(rol__nombre='Trabajador')

        # Renderizar los partials de las tablas filtradas
        html_tareas = render_to_string('partials/tabla_tareas.html', {'tareas': tareas, 'trabajadores': trabajadores}) 
        html_asignaciones = render_to_string('partials/tabla_asignaciones.html', {'asignaciones': asignaciones, 'trabajadores': trabajadores})

        return JsonResponse({'html_tareas': html_tareas, 'html_asignaciones': html_asignaciones})
    return JsonResponse({'error': 'Solicitud no válida.'}, status=400)



def reportes_tareas(request):
    trabajadores = Usuarios.objects.filter(rol__nombre='Trabajador')
    return render(request, 'reportes_tareas.html', {'trabajadores': trabajadores})

def get_report_data(request):
    chart_type = request.GET.get('chartType')
    worker_id = request.GET.get('workerId')
    filter_date = request.GET.get('filterDate')

    # Filtro por fecha
    if filter_date:
        try:
            start_date = parse_date(filter_date + '-01')
            end_date = parse_date(filter_date + '-31')
        except ValueError:
            return JsonResponse({'error': 'Formato de fecha no válido'}, status=400)
        
    response_data = []

    if worker_id:
        data = data.filter(trabajador__rut=worker_id)
    if filter_date:
        data = data.filter(fecha__range=[start_date, end_date])

    if chart_type == 'tareas-prioridad':
        data = Tareas.objects.values('prioridad').annotate(count=Count('prioridad'))
        response_data = [{'name': item['prioridad'], 'y': item['count']} for item in data]

    elif chart_type == 'asignaciones-estado':
        data = Asignacion.objects.values('estado').annotate(count=Count('estado'))
        response_data = [{'name': item['estado'], 'y': item['count']} for item in data]

    elif chart_type == 'tareas-asignadas':
        total_tareas = Tareas.objects.count()
        asignadas_count = Asignacion.objects.count()
        no_asignadas_count = total_tareas - asignadas_count
        response_data = [
            {'name': 'Asignadas', 'y': asignadas_count},
            {'name': 'No Asignadas', 'y': no_asignadas_count}
        ]

    elif chart_type == 'avance-trabajador':
        data = Asignacion.objects.values('trabajador__rut', 'trabajador__nombre', 'trabajador__apellido_p', 'trabajador__apellido_m').annotate(
            completadas=Count('id', filter=Q(estado='Completada'))
        )
        response_data = [{'name': f"{item['trabajador__nombre']} {item['trabajador__apellido_p']} {item['trabajador__apellido_m']}", 'y': item['completadas']} for item in data]

    elif chart_type == 'tiempo-finalizacion':
        data = Asignacion.objects.annotate(month=TruncMonth('actualizado_en')).values('month').annotate(
            avg_time=Avg(F('actualizado_en') - F('asignado_en'))
        )
        response_data = [{'name': item['month'].strftime('%B'), 'y': item['avg_time'].days} for item in data]

    elif chart_type == 'tareas-mes':
        data = Tareas.objects.annotate(month=TruncMonth('creado_en')).values('month').annotate(count=Count('id'))
        response_data = [{'name': item['month'].strftime('%B'), 'y': item['count']} for item in data]

    return JsonResponse(response_data, safe=False)


def obtener_tabla_asignaciones(request):
    asignaciones = Asignacion.objects.all()
    trabajadores = Usuarios.objects.filter(rol__nombre='Trabajador')  # Asegurarse de que los trabajadores estén en el contexto
    html = render_to_string('partials/tabla_asignaciones.html', {
        'asignaciones': asignaciones,
        'trabajadores': trabajadores,
    })
    return JsonResponse({'html': html})


def obtener_tabla_tareas(request):
    tareas_asignadas_ids = Asignacion.objects.values_list('tarea_id', flat=True)
    tareas = Tareas.objects.exclude(id__in=tareas_asignadas_ids)  # Excluir tareas asignadas
    trabajadores = Usuarios.objects.filter(rol__nombre='Trabajador')  # Asegurarse de que los trabajadores estén en el contexto
    html = render_to_string('partials/tabla_tareas.html', {
        'tareas': tareas,
        'trabajadores': trabajadores,
    })
    return JsonResponse({'html': html})

    ##gabriel

def index(request):
    return render(request, 'index.html')

def add_page(request):
    return render(request, 'add_info.html')

def delete_page(request):
    return render(request, 'delete_info.html')

def edit_page(request):
    return render(request, 'edit_info.html')

@require_POST
def perform_add(request):
    if request.method == 'POST':
        # Obtén los datos del formulario
        rut = request.POST.get('rut')
        nombre = request.POST.get('nombre')
        apellido_p = request.POST.get('apellido_p')
        apellido_m = request.POST.get('apellido_m')
        fecha_n = request.POST.get('fecha_n')
        cod_rol = request.POST.get('cod_rol')  # Aquí estamos asumiendo que en el HTML se usa "cod_rol"
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        password = request.POST.get('password')

        # Verifica si el Rut o el correo ya existen en la base de datos
        if Usuarios.objects.filter(Q(rut=rut) | Q(correo=correo)).exists():
            return HttpResponse('Error: El Rut del usuario o el correo ya están registrados.', status=400)

        # Busca el rol por ID (cod_rol)
        rol = Rol.objects.get(id_rol=cod_rol)

        # Inserta los nuevos datos en la base de datos
        nuevo_trabajador = Usuarios(
            rut=rut,
            nombre=nombre,
            apellido_p=apellido_p,
            apellido_m=apellido_m,
            fecha_n=fecha_n,
            rol=rol,  # Asegúrate de pasar el objeto rol aquí
            correo=correo,
            telefono=telefono,
        )

        # Hashea la contraseña y guárdala
        nuevo_trabajador.set_password(password)
        nuevo_trabajador.save()

        # Redirige a la página de éxito después de agregar los datos
        return render(request, 'success_add.html')
    else:
        # Si no es una solicitud POST, redirigir al formulario de agregar
        return redirect('add_page')
    
@require_POST
def perform_delete(request):
    full_name = request.POST.get('fullName')
    
    # Verificar si el full_name está presente
    if not full_name:
        return JsonResponse({'success': False, 'message': 'Nombre completo no proporcionado.'}, status=400)

    parts = full_name.split(' ')
    
    # Validar que el nombre completo tenga al menos tres partes
    if len(parts) < 3:
        return JsonResponse({'success': False, 'message': 'Nombre completo inválido.'}, status=400)

    apellido_m = parts.pop()
    apellido_p = parts.pop()
    nombre = ' '.join(parts)

    try:
        trabajador = Usuarios.objects.get(nombre=nombre, apellido_p=apellido_p, apellido_m=apellido_m)
        trabajador.delete()

        # Redirigir a la vista de éxito después de la eliminación
        return JsonResponse({'success': True})
    except Usuarios.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'No se encontró el trabajador con ese nombre completo.'}, status=404)

def success_delete(request):
    return render(request, 'success_delete.html')
#### ------------------------------------------------edit---------------------------------------------
def get_user_data(request):
    full_name = request.GET.get('fullName')
    if not full_name:
        return HttpResponse('El nombre es obligatorio.', status=400)

    # Separar el fullName en nombre, apellido paterno y apellido materno
    try:
        nombre, apellido_p, apellido_m = full_name.split()
    except ValueError:
        return HttpResponse('El formato del nombre no es válido.', status=400)

    try:
        # Buscar el usuario en la base de datos
        usuario = Usuarios.objects.get(nombre=nombre, apellido_p=apellido_p, apellido_m=apellido_m)
        user_data = {
            'rut': usuario.rut,
            'nombre': usuario.nombre,
            'apellido_p': usuario.apellido_p,
            'apellido_m': usuario.apellido_m,
            'fecha_n': usuario.fecha_n,
            #'rol': usuario.rol,  
            'correo': usuario.correo,
            'telefono': usuario.telefono,
        }
        return JsonResponse(user_data)
    except Usuarios.DoesNotExist:
        return HttpResponse('Usuario no encontrado.', status=404)
@require_POST
def edit_data(request):
    original_id = request.POST.get('originalId')
    new_id = request.POST.get('rut')  # coincide con el nombre en tu HTML
    new_name = request.POST.get('nombre')
    new_last_name = request.POST.get('apellido_p')
    new_mother_last_name = request.POST.get('apellido_m')
    new_date = request.POST.get('fecha_n')
    new_email = request.POST.get('correo')
    new_telefono = request.POST.get('telefono')

    try:
        # Obtenemos el trabajador original
        trabajador = Usuarios.objects.get(rut=original_id)

        # Verificamos si hay cambios en los campos
        if (trabajador.rut == new_id and
            trabajador.nombre == new_name and
            trabajador.apellido_p == new_last_name and
            trabajador.apellido_m == new_mother_last_name and
            str(trabajador.fecha_n) == new_date and  # convertimos fecha a str para comparar
            trabajador.correo == new_email and
            trabajador.telefono == new_telefono):
            
            return JsonResponse({'error': 'No se han realizado cambios'}, status=400)

        # Verificar si el nuevo RUT ya existe
        if new_id != original_id and Usuarios.objects.filter(rut=new_id).exists():
            return JsonResponse({'error': 'El RUT ya está en uso por otro trabajador.'}, status=400)

        # Actualizar los campos del trabajador
        trabajador.rut = new_id
        trabajador.nombre = new_name
        trabajador.apellido_p = new_last_name
        trabajador.apellido_m = new_mother_last_name
        
        # Convertir la fecha de string a objeto de fecha
        trabajador.fecha_n = datetime.strptime(new_date, '%Y-%m-%d').date()

        trabajador.correo = new_email
        trabajador.telefono = new_telefono
        trabajador.save()

        messages.success(request, "Los cambios se han guardado correctamente.")
        return JsonResponse({'success': True})  # Puedes también usar redirect aquí si prefieres

    except Usuarios.DoesNotExist:
        return JsonResponse({'error': 'No se encontró el trabajador para actualizar.'}, status=404)

    except IntegrityError as e:
        return JsonResponse({'error': f'Error al guardar los datos: {str(e)}'}, status=400)

def get_names(request):
    trabajadores_list = Usuarios.objects.all()
    names = [f"{t.nombre} {t.apellido_p} {t.apellido_m}" for t in trabajadores_list]
    return JsonResponse(names, safe=False)

def success_edit(request):
    return render(request, 'success_edit.html')

#------------------------------------TABLA TRABAJADORES-------

#------------------------------------DASHBOARD----------------
from django.db.models import Count
from django.http import JsonResponse
from .models import Reportes_Problemas, Usuarios

def dashboard(request):
    # Obtener los datos de reportes
    incidentes = Reportes_Problemas.objects.all()
    
    # Obtener todos los trabajadores
    trabajadores_list = Usuarios.objects.all()

    # Filtrar incidentes por tipo
    tipo_incidentes = incidentes.values('tipo_incidente').annotate(count=Count('id'))
    tipos = [tipo['tipo_incidente'] for tipo in tipo_incidentes]
    counts = [tipo['count'] for tipo in tipo_incidentes]

    # Obtener marcos únicos desde el modelo reportes_problemas
    marcos = incidentes.values_list('marco', flat=True).distinct()

    # Calcular el promedio de incidentes por mes
    num_meses = incidentes.dates('fecha_reporte', 'month').count()  # Cambia 'fecha_reporte' por el campo que usas para las fechas
    total_reportes = incidentes.count()
    promedio_reportes_por_mes = total_reportes / num_meses if num_meses > 0 else 0

    context = {
        'tipos': tipos,
        'counts': counts,
        'marcos': marcos,
        'trabajadores': trabajadores_list,
        'promedio_reportes_por_mes': promedio_reportes_por_mes,  # KPI añadido
    }

    # Verificar si la solicitud es AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Filtrar por tipo y marco si se recibe un request AJAX
        tipo_seleccionado = request.GET.get('tipo')
        marco_seleccionado = request.GET.get('marco')
        trabajador_seleccionado = request.GET.get('trabajador')
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')

        if tipo_seleccionado:
            incidentes = incidentes.filter(tipo_incidente=tipo_seleccionado)

        if marco_seleccionado and marco_seleccionado != 'Todos':
            incidentes = incidentes.filter(marco=marco_seleccionado)

        if trabajador_seleccionado:
            incidentes = incidentes.filter(rut_usuario__rut=trabajador_seleccionado)

        if fecha_inicio and fecha_fin:
            incidentes = incidentes.filter(fecha_reporte__range=[fecha_inicio, fecha_fin])

        tipo_incidentes = incidentes.values('tipo_incidente').annotate(count=Count('id'))
        tipos = [tipo['tipo_incidente'] for tipo in tipo_incidentes]
        counts = [tipo['count'] for tipo in tipo_incidentes]

        # Calcular el porcentaje para los incidentes filtrados
        total_incidentes = sum(counts)
        porcentajes = [(count / total_incidentes * 100) if total_incidentes > 0 else 0 for count in counts]

        return JsonResponse({'tipos': tipos, 'counts': counts, 'porcentajes': porcentajes})

    return render(request, 'dashboard.html', context)

def filtrar_reportes(request):
    # Obtener los filtros del request
    trabajador = request.GET.get('trabajador')
    marco = request.GET.get('marco')
    tipo_incidente = request.GET.get('tipo_incidente')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    # Inicializar la queryset
    reportes = Reportes_Problemas.objects.all()

    # Aplicar filtros
    if trabajador:
        reportes = reportes.filter(rut_usuario__rut=trabajador)

    if marco:
        reportes = reportes.filter(marco=marco)

    if tipo_incidente:
        reportes = reportes.filter(tipo_incidente=tipo_incidente)

    if fecha_inicio and fecha_fin:
        reportes = reportes.filter(fecha_reporte__range=[fecha_inicio, fecha_fin])

    # Obtener las categorías de incidentes de forma dinámica
    categorias = reportes.values('tipo_incidente').distinct()
    categorias = [cat['tipo_incidente'] for cat in categorias]

    # Obtener las series de datos dinámicamente
    series = [reportes.filter(tipo_incidente=categoria).count() for categoria in categorias]

    # Datos para gráfico de desempeño por trabajadores a lo largo del tiempo
    fechas_reporte = reportes.dates('fecha_reporte', 'month', order='ASC')
    trabajadores_series = []

    for trabajador in Usuarios.objects.all():
        data = []
        for fecha in fechas_reporte:
            count = reportes.filter(rut_usuario=trabajador, fecha_reporte__year=fecha.year, fecha_reporte__month=fecha.month).count()
            data.append(count)
        trabajadores_series.append({
            'name': f"{trabajador.nombre} {trabajador.apellido_p} {trabajador.apellido_m}",
            'data': data
        })

    return JsonResponse({
        'categorias': categorias,
        'series': series,
        'fechas_reporte': [fecha.strftime('%Y-%m') for fecha in fechas_reporte],
        'trabajadores_series': trabajadores_series
    })

#----------------------------------nuevo gestion usuarios----------------
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Usuarios 

def gestion_usuarios(request):
    return render(request, 'gestion_usuarios.html')

def eliminar_usuario(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        usuario_rut = request.POST.get('rut')

        try:
            usuario = Usuarios.objects.get(rut=usuario_rut)
            usuario.delete()

            return JsonResponse({
                'message': 'Usuario eliminado correctamente.',
                'rut': usuario_rut,
            })
        except Usuarios.DoesNotExist:
            return JsonResponse({'error': 'El usuario no existe.'}, status=404)
    return JsonResponse({'error': 'Solicitud no válida.'}, status=400)

def editar_usuario(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        usuario_rut = request.POST.get('rut')
        nombre = request.POST.get('nombre')
        apellido_p = request.POST.get('apellido_p')
        apellido_m = request.POST.get('apellido_m')
        fecha_n = request.POST.get('fecha_n')
        rol = request.POST.get('rol')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')

        try:
            usuario = Usuarios.objects.get(rut=usuario_rut)
            usuario.nombre = nombre
            usuario.apellido_p = apellido_p
            usuario.apellido_m = apellido_m
            usuario.fecha_n = fecha_n
            usuario.rol = rol
            usuario.correo = correo
            usuario.telefono = telefono
            usuario.save()

            return JsonResponse({
                'message': 'Usuario actualizado correctamente.',
                'rut': usuario_rut,
                'nombre': usuario.nombre,
                'apellido_p': usuario.apellido_p,
                'apellido_m': usuario.apellido_m,
                'fecha_n' : usuario.fecha_n,
                'rol' : usuario.rol,
                'correo' : usuario.correo,
                'telefono': usuario.telefono,
            })
        except Usuarios.DoesNotExist:
            return JsonResponse({'error': 'El usuario no existe.'}, status=404)
    return JsonResponse({'error': 'Solicitud no válida.'}, status=400)

def crear_usuario(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        rut = request.POST.get('rut')
        nombre = request.POST.get('nombre')
        apellido_p = request.POST.get('apellido_p')
        apellido_m = request.POST.get('apellido_m')
        fecha_n = request.POST.get('fecha_n')
        rol = request.POST.get('rol')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        password = request.POST.get('password')

        if not rut or not nombre or not telefono:
            return JsonResponse({'error': 'Faltan datos obligatorios.'}, status=400)

        # Crear nuevo usuario
        usuario = Usuarios.objects.create(
            rut=rut,
            nombre=nombre,
            apellido_p=apellido_p,
            apellido_m=apellido_m,
            fecha_n=fecha_n,
            rol=rol,
            correo=correo,
            telefono=telefono,
            password=password
            # Rellena otros campos según sea necesario
        )

        # Opcional: Recargar la lista de usuarios
        usuarios = Usuarios.objects.all()
        html = render_to_string('partials/tabla_usuarios.html', {'usuarios': usuarios})

        return JsonResponse({'message': 'Usuario creado correctamente.', 'html': html})
    return JsonResponse({'error': 'Solicitud no válida.'}, status=400)

def inicio_admin(request):
    return render(request, 'inicio_admin.html')