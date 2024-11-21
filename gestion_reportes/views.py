from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.generic import CreateView
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.db.models import Q, Count, Avg, F
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Tareas, Reportes_Problemas, Asignacion
from gestion_datos.models import Usuarios, Problemas, Marcos
from .forms import ReporteForm
import os
from twilio.rest import Client


import tempfile
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_to_drive(file):
    google_credentials = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
    creds = service_account.Credentials.from_service_account_info(
        google_credentials, scopes=["https://www.googleapis.com/auth/drive.file"]
    )

    service = build('drive', 'v3', credentials=creds)

    folder_id = '1tF5rKetujaSi0zbCuDL-GcU05PxLdHQz' 

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file.read())
        temp_file_path = temp_file.name

    file_metadata = {
        'name': file.name,
        'parents': [folder_id]
    }

    media = MediaFileUpload(temp_file_path, mimetype=file.content_type)
    uploaded_file = service.files().create(
        body=file_metadata, media_body=media, fields='id'
    ).execute()

    os.remove(temp_file_path)

    file_id = uploaded_file.get('id')
    file_link = f"https://drive.google.com/uc?id={file_id}"
    
    return file_link

#anto
def enviar_notificacion_tarea(trabajador, tarea):
    mensaje = (
        f"Tienes una nueva tarea asignada: \n"
        f"Descripción: {tarea.descripcion}\n"
        f"Prioridad: {tarea.prioridad}"
    )

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=mensaje,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=trabajador.telefono
    )
    
@require_POST
def eliminar_reporte(request, reporte_id):
    try:
        reporte = Reportes_Problemas.objects.get(id=reporte_id)
        reporte.delete()
        return JsonResponse({'success': True})
    except Reportes_Problemas.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Reporte no encontrado'})

def ver_imagen(request, reporte_id):
    reporte = get_object_or_404(Reportes_Problemas, id=reporte_id)
    return render(request, 'ver_imagen.html', {'reporte': reporte})

#class crearTareaView(CreateView):
#    model=Tareas
#    template_name=lista_tareas.html
#    success_url="/"
#    fields='__all__'



#anto
def reporte(request):
    return render(request, 'reporte.html')

def reporte_trabajador(request):
    rut_usuario = request.user.rut 
    reportes = Reportes_Problemas.objects.filter(rut=rut_usuario).order_by('-fecha_creacion') 
    return render(request, 'reportes_trabajador.html', {'reportes': reportes})

def reporte_exito(request):
    return render(request, 'reporte_exito.html')
def reporte_view(request):
    trabajadores = Usuarios.objects.filter(rol__id_rol=2)
    marcos = Marcos.objects.all() 
    tipos_incidente = Problemas.objects.all() 

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
            foto_url = upload_to_drive(foto_url) if foto_url else None
            tipo_incidente_obj = Problemas.objects.get(id=tipo_incidente)
            marcos_obj = Marcos.objects.get(id=marco) 


            
            nuevo_reporte = Reportes_Problemas(
                rut_usuario=usuario,
                tipo_incidente=tipo_incidente_obj,
                descripcion=descripcion,
                marco=marcos_obj,
                medida_marco=medida_marco,
                foto_url=foto_url,
                fecha_reporte=timezone.now(),
                latitud=latitud,
                longitud=longitud
            )
            nuevo_reporte.save()

            administradores = Usuarios.objects.filter(rol__id_rol=1)

            mensaje = (
                f'{usuario.nombre} {usuario.apellido_p} {usuario.apellido_m} '
                f'ha reportado {tipo_incidente_obj.nombre}.\nDescripción: {descripcion}\nMarco: {marcos_obj.nombre}\nFecha: {nuevo_reporte.fecha_reporte.strftime("%Y-%m-%d")}'
            )

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            for admin in administradores:
                client.messages.create(
                    body=mensaje,
                    from_= settings.TWILIO_PHONE_NUMBER,
                    to= admin.telefono
                )

            return redirect('gestion_reportes:reporte_exito') 

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

def ver_reportes(request):
    ordenar = request.GET.get('ordenar', 'asc')

    if ordenar == 'asc':
        reportes = Reportes_Problemas.objects.all().order_by('fecha_reporte')
    else:
        reportes = Reportes_Problemas.objects.all().order_by('-fecha_reporte')
    
    # Configuración de paginación
    paginador = Paginator(reportes, 10)  # Cambia 10 al número de registros por página que desees
    pagina = request.GET.get('page')  # Captura el número de la página actual desde la URL
    reportes_paginados = paginador.get_page(pagina)  # Obtiene los reportes de la página actual
    
    context = {
        'reportes': reportes_paginados  # Usa los reportes paginados en lugar de todos los reportes
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
            return redirect('gestion_reportes:ver_reportes')
        else:
            print(form.errors)
    else:
        form = ReporteForm(instance=reporte)

    return render(request, 'editar_reporte.html', {'form': form, 'reporte': reporte})
###benja

def lista_tareas(request):
    tareas_asignadas_ids = Asignacion.objects.values_list('tarea_id', flat=True)
    tareas = Tareas.objects.exclude(id__in=tareas_asignadas_ids).filter(es_predeterminado=False)
    tareas_predeterminadas = Tareas.objects.filter(es_predeterminado=True)
    trabajadores = Usuarios.objects.filter(rol__nombre='Usuario') 
    asignaciones = Asignacion.objects.all()

    return render(request, 'lista_tareas.html', {
        'tareas': tareas,
        'tareas_predeterminadas': tareas_predeterminadas,
        'trabajadores': trabajadores,
        'asignaciones': asignaciones,
    })


def obtener_reportes_problemas_disponibles(request):
    reportes_asignados_ids = Tareas.objects.exclude(id_reporte__isnull=True).values_list('id_reporte', flat=True)
    
    reportes_disponibles = Reportes_Problemas.objects.select_related('tipo_incidente').exclude(id__in=reportes_asignados_ids)


    reportes_data = [
        {
            'id': reporte.id,
            'tipo_incidente': reporte.tipo_incidente.nombre, 
            'fecha_reporte': reporte.fecha_reporte.strftime('%Y-%m-%d'),
            'descripcion': reporte.descripcion
        }
        for reporte in reportes_disponibles
    ]

    return JsonResponse(reportes_data, safe=False)


def asignar_tarea_ajax(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        tarea_id = request.POST.get('tarea_id')
        trabajador_id = request.POST.get('trabajador_id')

        if not tarea_id or not trabajador_id:
            return JsonResponse({'error': 'Faltan datos de la tarea o trabajador.'}, status=400)

        try:
            tarea = Tareas.objects.get(id=tarea_id)
            trabajador = Usuarios.objects.get(rut=trabajador_id, rol__nombre='Usuario')

            asignacion = Asignacion.objects.create(tarea=tarea, trabajador=trabajador, estado='En espera')
            enviar_notificacion_tarea(trabajador, tarea)

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

            trabajadores = Usuarios.objects.filter(rol__nombre='Usuario')
            trabajadores_data = [{'id': trabajador.rut, 'nombre': trabajador.full_name()} for trabajador in trabajadores]

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
            trabajador = Usuarios.objects.get(rut=trabajador_id, rol__nombre='Usuario')
            
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

            trabajadores = Usuarios.objects.filter(rol__nombre='Usuario')
            trabajadores_data = [{'id': trabajador.rut, 'nombre': trabajador.full_name()} for trabajador in trabajadores]

            return JsonResponse({
                'message': 'Tarea actualizada correctamente.',
                'tarea_id': tarea_id,
                'nombre': tarea.nombre,
                'descripcion': tarea.descripcion,
                'prioridad': tarea.prioridad,
                'trabajadores': trabajadores_data, 
            })
        except Tareas.DoesNotExist:
            return JsonResponse({'error': 'La tarea no existe.'}, status=404)
    return JsonResponse({'error': 'Solicitud no válida.'}, status=400)

def obtener_tareas_predeterminadas(request):
    tareas = Tareas.objects.filter(es_predeterminado=True)
    tareas_data = [
        {
            'id': tarea.id,
            'nombre': tarea.nombre,
            'descripcion': tarea.descripcion,
            'prioridad': tarea.prioridad
        }
        for tarea in tareas
    ]
    return JsonResponse({'tareas': tareas_data})

def crear_tarea_ajax(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        prioridad = request.POST.get('prioridad')
        id_reporte = request.POST.get('id_reporte') 
        es_predeterminado = request.POST.get('es_predeterminado') == 'true'

        if not nombre or not prioridad:
            return JsonResponse({'error': 'Faltan datos obligatorios.'}, status=400)

        try:
            reporte = Reportes_Problemas.objects.get(id=id_reporte) if id_reporte else None

            tarea = Tareas.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                prioridad=prioridad,
                id_reporte=reporte,
                es_predeterminado=es_predeterminado
            )

            tareas_asignadas_ids = Asignacion.objects.values_list('tarea_id', flat=True)
            tareas = Tareas.objects.exclude(id__in=tareas_asignadas_ids).filter(es_predeterminado=False)
            html = render_to_string('partials/tabla_tareas.html', {'tareas': tareas})

            return JsonResponse({'message': 'Tarea creada correctamente.', 'html': html})
        except Reportes_Problemas.DoesNotExist:
            return JsonResponse({'error': 'El reporte seleccionado no existe.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Solicitud no válida.'}, status=400)

def filtrar_tareas_ajax(request):
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        filter_name = request.GET.get('filterName', '')
        filter_priority = request.GET.get('filterPriority', '')
        filter_state = request.GET.get('filterState', '')
        filter_worker = request.GET.get('filterWorker', '')
        hide_completed = request.GET.get('hideCompleted', 'off') == 'on'

        tareas_asignadas_ids = Asignacion.objects.values_list('tarea_id', flat=True)
        tareas = Tareas.objects.exclude(id__in=tareas_asignadas_ids).filter(es_predeterminado=False)
                
        print("hide_completed:", hide_completed)
        print("filter_state:", filter_state)

        if filter_name:
            tareas = tareas.filter(nombre__icontains=filter_name)
        if filter_priority:
            tareas = tareas.filter(prioridad=filter_priority)

        asignaciones = Asignacion.objects.all()
        for asignacion in asignaciones:
            print("Estado de la tarea", asignacion.tarea.nombre, ":", asignacion.estado)

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

        trabajadores = Usuarios.objects.filter(rol__nombre='Usuario')

        html_tareas = render_to_string('partials/tabla_tareas.html', {'tareas': tareas, 'trabajadores': trabajadores}) 
        html_asignaciones = render_to_string('partials/tabla_asignaciones.html', {'asignaciones': asignaciones, 'trabajadores': trabajadores})

        return JsonResponse({'html_tareas': html_tareas, 'html_asignaciones': html_asignaciones})
    return JsonResponse({'error': 'Solicitud no válida.'}, status=400)

def obtener_tabla_asignaciones(request):
    asignaciones = Asignacion.objects.all()
    trabajadores = Usuarios.objects.filter(rol__nombre='Usuario') 
    html = render_to_string('partials/tabla_asignaciones.html', {
        'asignaciones': asignaciones,
        'trabajadores': trabajadores,
    })
    return JsonResponse({'html': html})


def obtener_tabla_tareas(request):
    tareas_asignadas_ids = Asignacion.objects.values_list('tarea_id', flat=True)
    tareas = Tareas.objects.exclude(id__in=tareas_asignadas_ids).filter(es_predeterminado=False)
    trabajadores = Usuarios.objects.filter(rol__nombre='Usuario') 
    html = render_to_string('partials/tabla_tareas.html', {
        'tareas': tareas,
        'trabajadores': trabajadores,
    })
    return JsonResponse({'html': html})

def obtener_tareas_predeterminadas2(request):
    tareas = Tareas.objects.filter(es_predeterminado=True)
    html = render_to_string('partials/tabla_tareas_predeterminadas.html', {'tareas_predeterminadas': tareas})
    return JsonResponse({'html': html})

def reportes_tareas(request):
    trabajadores = Usuarios.objects.filter(rol__nombre='Usuario')
    return render(request, 'reportes.html', {'trabajadores': trabajadores})

def get_report_data(request):
    chart_type = request.GET.get('chartType')
    worker_id = request.GET.get('workerId')
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')

    data = Tareas.objects.all() 

    if worker_id:
        data = data.filter(asignacion__trabajador__rut=worker_id)

    if start_date and end_date:
        data = data.filter(creado_en__range=[start_date, end_date])
    elif start_date:
        data = data.filter(fecha__gte=start_date)
    elif end_date:
        data = data.filter(fecha__lte=end_date)

    if chart_type == 'tareas-prioridad':
        data = data.exclude(asignacion__estado='Completada')
        filtered_data = data.values('prioridad').annotate(count=Count('prioridad'))
        response_data = [{'name': item['prioridad'], 'y': item['count']} for item in filtered_data]

    elif chart_type == 'asignaciones-estado':
        data = Asignacion.objects.all()  
        if worker_id:
            data = data.filter(trabajador__rut=worker_id)  
        if start_date and end_date:
            data = data.filter(asignado_en__range=[start_date, end_date]) 
        elif start_date:
            data = data.filter(fecha__gte=start_date)
        elif end_date:
            data = data.filter(fecha__lte=end_date)

        data = data.values('estado').annotate(count=Count('estado'))  
        response_data = [{'name': item['estado'], 'y': item['count']} for item in data]


    elif chart_type == 'tareas-asignadas':
        data = data  
        asignadas_count = Asignacion.objects.filter(~Q(estado='Completada'), tarea__in=data).count()  
        asignadas_count1 = Asignacion.objects.filter(tarea__in=data).count() 
        no_asignadas_count = data.count() - asignadas_count1  

        response_data = [
            {'name': 'Asignadas', 'y': asignadas_count},
            {'name': 'No Asignadas', 'y': no_asignadas_count}
        ]

    elif chart_type == 'avance-trabajador':
        data = Asignacion.objects.all()
        if worker_id:
            data = data.filter(trabajador__rut=worker_id)  
        if start_date and end_date:
            data = data.filter(asignado_en__range=[start_date, end_date])  
        elif start_date:
            data = data.filter(asignado_en__gte=start_date)
        elif end_date:
            data = data.filter(asignado_en__lte=end_date)

        data = data.values('trabajador__rut', 'trabajador__nombre', 'trabajador__apellido_p', 'trabajador__apellido_m').annotate(
            completadas=Count('id', filter=Q(estado='Completada'))
        )
        response_data = [{'name': f"{item['trabajador__nombre']} {item['trabajador__apellido_p']} {item['trabajador__apellido_m']}", 'y': item['completadas']} for item in data]

    elif chart_type == 'tiempo-finalizacion':
        data = Asignacion.objects.all()  
        if worker_id:
            data = data.filter(trabajador__rut=worker_id) 
        if start_date and end_date:
            data = data.filter(asignado_en__range=[start_date, end_date])  
        elif start_date:
            data = data.filter(asignado_en__gte=start_date)
        elif end_date:
            data = data.filter(asignado_en__lte=end_date)

        data = data.annotate(month=TruncMonth('actualizado_en')).values('month').annotate(
            avg_time=Avg(F('actualizado_en') - F('asignado_en'))
        )
        response_data = [{'name': item['month'].strftime('%B'), 'y': item['avg_time'].days} for item in data]

    elif chart_type == 'tareas-mes':
        data = data  
        data = data.annotate(month=TruncMonth('creado_en')).values('month').annotate(count=Count('id'))
        response_data = [{'name': item['month'].strftime('%B'), 'y': item['count']} for item in data]

    return JsonResponse(response_data, safe=False)
