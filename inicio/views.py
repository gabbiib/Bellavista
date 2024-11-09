import random
import string
from datetime import datetime
import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import send_mail, EmailMessage
from django.db import IntegrityError
from django.db.models import Q, Count, Avg, F, Value
from django.db.models.functions import Concat, TruncMonth
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.dateparse import parse_date
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from gestion_datos.models import Usuarios, Problemas, Marcos
from gestion_reportes.models import Asignacion, Reportes_Problemas
from .forms import RecuperarContrasenaForm, ContactarAdminForm
from twilio.rest import Client

def reporte_view(request):
    trabajadores = Usuarios.objects.filter(rol__id_rol=2)
    marcos = Marcos.objects.all()  # Obtenemos todos los marcos
    tipos_incidente = Problemas.objects.all()  # Obtenemos todos los tipos de incidente

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
                    from_= settings.TWILIO_PHONE_NUMBER,
                    to= admin.telefono
                )

            return redirect('reporte_exito') 

        except Usuarios.DoesNotExist:
            return render(request, 'reporte.html', {
                'trabajadores': trabajadores,
                'marcos': marcos,
                'tipos_incidente': tipos_incidente,
                'error': 'Usuario no encontrado.'
            })

    return render(request, 'reporte.html', {
        'trabajadores': trabajadores,
        'marcos': marcos,
        'tipos_incidente': tipos_incidente
    })

def inicio_admin(request):
    return render(request, 'inicio_admin.html')

def logout_view(request):
    response = LogoutView.as_view()(request)
    return response

def inicio(request):
    return render(request, 'inicio.html')

def actualizar_tarea(request, tarea_id):
    tarea = Asignacion.objects.get(tarea_id=tarea_id)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        tarea.estado = nuevo_estado
        tarea.save()  
        return redirect('trabajador') 
    
    return render(request, 'actualizar_tarea.html', {'tarea': tarea})

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

        # Validar el nuevo teléfono: debe tener 8 dígitos numéricos
        if nuevo_telefono and nuevo_telefono.isdigit() and len(nuevo_telefono) == 8:
            if nuevo_telefono != usuario.telefono[-8:]:  # Comparar solo los últimos 8 dígitos
                usuario.telefono = f'+569{nuevo_telefono}'
                telefono_cambiado = True
        elif nuevo_telefono:
            messages.error(request, 'El teléfono debe contener exactamente 8 dígitos.')

        # Validación de la nueva contraseña con regex
        password_regex = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*()_+={}\[\]|;:'\",<.>/?])(?=.*[A-Z]).{8,}$")
        if nueva_contrasena and password_regex.match(nueva_contrasena):
            usuario.set_password(nueva_contrasena)  # Cambia la contraseña usando set_password
            contrasena_cambiada = True
        elif nueva_contrasena:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres, incluir una letra mayúscula, un número y un carácter especial.')

        # Guardar solo si hubo algún cambio válido
        if telefono_cambiado or contrasena_cambiada:
            usuario.save()

            # Mantener la sesión si la contraseña ha cambiado
            if contrasena_cambiada:
                update_session_auth_hash(request, usuario)

        # Mensajes de éxito o información
        if telefono_cambiado and contrasena_cambiada:
            messages.success(request, 'Tu teléfono y contraseña han sido actualizados.')
        elif telefono_cambiado:
            messages.success(request, 'Tu teléfono ha sido actualizado.')
        elif contrasena_cambiada:
            messages.success(request, 'Tu contraseña ha sido actualizada.')
        else:
            messages.info(request, 'No se realizaron cambios.')

        return redirect('inicio:editar_perfil')

    contexto = {'telefono_actual': usuario.telefono}
    return render(request, 'editar_perfil.html', contexto)

def recuperar_contrasena(request):
    return render(request, 'recuperar_contrasena.html')

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
                        return redirect('inicio:trabajador')  
                    elif usuario.rol.id_rol == 1:
                        return redirect('inicio:inicio_admin')  
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

def recuperar_contrasena(request):
    return render(request, 'recuperar_contrasena.html')

def enviar_enlace_view(request):
    if request.method == 'POST':
        rut = request.POST.get('rut')
        try:
            usuario = Usuarios.objects.get(rut=rut)
            codigo_recuperacion = generar_codigo()
            
            usuario.codigo_recuperacion = codigo_recuperacion
            usuario.save()
            
            enlace_recuperacion = request.build_absolute_uri(
                reverse('inicio:recuperar_contrasena_codigo', args=[codigo_recuperacion])
            )
            
            mensaje = f"Hola {usuario.nombre},\n\nAquí está el enlace para recuperar tu contraseña: {enlace_recuperacion}\n\nEste enlace es válido por 1 hora."

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            
            client.messages.create(
                body=mensaje,
                from_= settings.TWILIO_PHONE_NUMBER,  
                to= usuario.telefono  
            )

            messages.success(request, 'Hemos enviado un enlace para recuperar tu contraseña a tu teléfono.')
            return redirect('inicio:recuperar_contrasena')  
            
        except Usuarios.DoesNotExist:
            messages.error(request, 'El RUT proporcionado no está asociado a ninguna cuenta.')
            return redirect('inicio:recuperar_contrasena')  
            
    return render(request, 'recuperar_contrasena.html')

def recuperar_contrasena_codigo(request, codigo):
    if request.method == 'POST':
        nueva_contrasena = request.POST.get('nueva_contrasena')
        try:
            usuario = get_object_or_404(Usuarios, codigo_recuperacion=codigo)

            usuario.password = make_password(nueva_contrasena)
            usuario.codigo_recuperacion = None  
            usuario.save()

            messages.success(request, 'Tu contraseña ha sido actualizada exitosamente.')
            return redirect('inicio:login')
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
        return redirect('inicio:recuperar_contrasena')
    return render(request, 'recuperar_contrasena.html')
