from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from gestion_reportes.models import Asignacion
from gestion_datos.models import Usuarios
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password, check_password
from twilio.rest import Client
from django.urls import reverse
from .forms import RecuperarContrasenaForm, ContactarAdminForm
from django.views.decorators.http import require_POST
import string
from django.contrib.auth.views import LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
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
from django.urls import reverse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .forms import RecuperarContrasenaForm, ContactarAdminForm
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
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



def inicio_admin(request):
    return render(request, 'inicio_admin.html')

def logout_view(request):
    response = LogoutView.as_view()(request)
    return response

def inicio(request):
    return render(request, 'inicio.html')

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
                        return redirect('inicio:administrador')  
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
                from_='whatsapp:' + settings.TWILIO_PHONE_NUMBER,  
                to='whatsapp:' + usuario.telefono  
            )

            messages.success(request, 'Hemos enviado un enlace para recuperar tu contraseña a tu WhatsApp.')
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
