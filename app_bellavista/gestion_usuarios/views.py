from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.db.models import Value, F
from django.db.models.functions import Concat
from django.db.models import Count, Value
from .models import reportes_problemas, trabajadores


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
        id_trabajador = request.POST.get('id_trabajador')
        nombre = request.POST.get('Nombre')
        apellido_p = request.POST.get('Apellido_P')
        apellido_m = request.POST.get('Apellido_M')
        fecha_n = request.POST.get('Fecha_N')
        cod_rol = request.POST.get('cod_rol')
        correo = request.POST.get('correo') 
        password = request.POST.get('password')

        # Verifica si el ID o el correo ya existen en la base de datos
        if trabajadores.objects.filter(Q(id_trabajador=id_trabajador) | Q(correo=correo)).exists():
            return HttpResponse('Error: El ID de trabajador o el correo ya están registrados.', status=400)

        # Inserta los nuevos datos
        nuevo_trabajador = trabajadores(
            id_trabajador=id_trabajador,
            Nombre=nombre,
            Apellido_P=apellido_p,
            Apellido_M=apellido_m,
            Fecha_N=fecha_n,
            cod_rol=cod_rol,
            correo=correo  
        )

        # Hashear la contraseña y guardarla
        nuevo_trabajador.set_password(password)

        nuevo_trabajador.save()

        # Redirige a la página de éxito después de agregar los datos
        return render(request, 'success_add.html')
    else:
        # Si no es una solicitud POST, redirigir al formulario de agregar
        return redirect('add_page')

def get_user_data(request):
    full_name = request.GET.get('fullName')
    if not full_name:
        return HttpResponse('Nombre es obligatorio.', status=400)

    try:
        # Split sin perder espacios en nombres compuestos
        nombres = full_name.split(' ')
        if len(nombres) < 3:
            return HttpResponse('Nombre completo inválido.', status=400)

        apellido_m = nombres.pop()
        apellido_p = nombres.pop()
        nombre = ' '.join(nombres)  # Restaura el nombre en caso de que tenga más de una palabra

        trabajador = trabajadores.objects.get(Nombre=nombre, Apellido_P=apellido_p, Apellido_M=apellido_m)
        
        data = {
            'id_trabajador': trabajador.id_trabajador,
            'Nombre': trabajador.Nombre,
            'Apellido_P': trabajador.Apellido_P,
            'Apellido_M': trabajador.Apellido_M,
            'Fecha_N': trabajador.Fecha_N,
            'cod_rol': trabajador.cod_rol,
            'correo': trabajador.correo,
        }
        return JsonResponse(data)
    except trabajadores.DoesNotExist:
        return HttpResponse('Usuario no encontrado', status=404)


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
        trabajador = trabajadores.objects.get(Nombre=nombre, Apellido_P=apellido_p, Apellido_M=apellido_m)
        trabajador.delete()

        # Redirigir a la vista de éxito después de la eliminación
        return JsonResponse({'success': True})
    except trabajadores.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'No se encontró el trabajador con ese nombre completo.'}, status=404)

def success_delete(request):
    return render(request, 'success_delete.html')

def get_names(request):
    trabajadores_list = trabajadores.objects.all()
    names = [f"{t.Nombre} {t.Apellido_P} {t.Apellido_M}" for t in trabajadores_list]
    return JsonResponse(names, safe=False)

@require_POST
def edit_data(request):
    original_id = request.POST.get('originalId')
    new_id = request.POST.get('newId')
    new_name = request.POST.get('newName')
    new_last_name = request.POST.get('newLastName')
    new_mother_last_name = request.POST.get('newMotherLastName')
    new_date = request.POST.get('newDate')
    new_role = request.POST.get('newRole')
    new_email = request.POST.get('newEmail')

    try:
        trabajador = trabajadores.objects.get(id_trabajador=original_id)
        trabajador.id_trabajador = new_id
        trabajador.Nombre = new_name
        trabajador.Apellido_P = new_last_name
        trabajador.Apellido_M = new_mother_last_name
        trabajador.Fecha_N = new_date
        trabajador.cod_rol = new_role
        trabajador.correo = new_email
        trabajador.save()
        return render(request, 'success_edit.html')
    except trabajadores.DoesNotExist:
        return HttpResponse('No se encontró el trabajador para actualizar.', status=404)


def get_usuarios(request):
    usuarios = trabajadores.objects.all()
    data = [{'id': usuario.id_trabajador, 'full_name': usuario.full_name()} for usuario in usuarios]
    return JsonResponse(data, safe=False)
    
def dashboard(request):
    # Obtener los datos de reportes
    incidentes = reportes_problemas.objects.all()
    # Obtener todos los trabajadores
    trabajadores_list = trabajadores.objects.all()

    # Filtrar incidentes por tipo
    tipo_incidentes = incidentes.values('tipo_incidente').annotate(count=Count('id'))
    tipos = [tipo['tipo_incidente'] for tipo in tipo_incidentes]
    counts = [tipo['count'] for tipo in tipo_incidentes]

    # Calcular el porcentaje de cada tipo de incidente
    total_incidentes = sum(counts)
    porcentajes = [(count / total_incidentes * 100) if total_incidentes > 0 else 0 for count in counts]

    # Marcas disponibles (mantener si es necesario en la plantilla)
    marcos = ['Marco 1', 'Marco 2', 'Marco 3', 'Marco 4', 'Marco 5', 'Marco 6']

    context = {
        'tipos': tipos,
        'counts': counts,
        'porcentajes': porcentajes,
        'marcos': marcos,
        'trabajadores': trabajadores_list,
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
            incidentes = incidentes.filter(rut_usuario__id_trabajador=trabajador_seleccionado)

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
    medida_marco = request.GET.get('medida_marco', None)
    trabajador = request.GET.get('trabajador', None)
    marco = request.GET.get('marco', None)
    tipo_incidente = request.GET.get('tipo_incidente', None)
    fecha_inicio = request.GET.get('fecha_inicio', None)
    fecha_fin = request.GET.get('fecha_fin', None)

    # Inicializar la queryset
    reportes = reportes_problemas.objects.all()

    # Aplicar filtros
    if medida_marco:
        reportes = reportes.filter(medida_marco=medida_marco)

    if trabajador:
        reportes = reportes.filter(
            id_trabajador__in=trabajadores.objects.annotate(
                nombre_completo=Concat('Nombre', Value(' '), 'Apellido_P', Value(' '), 'Apellido_M')
            ).filter(nombre_completo__icontains=trabajador)
        )

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

    for trabajador in trabajadores.objects.all():
        data = []
        for fecha in fechas_reporte:
            count = reportes.filter(rut_usuario=trabajador, fecha_reporte__year=fecha.year, fecha_reporte__month=fecha.month).count()
            data.append(count)
        trabajadores_series.append({
            'name': f"{trabajador.Nombre} {trabajador.Apellido_P} {trabajador.Apellido_M}",
            'data': data
        })

    return JsonResponse({
        'categorias': categorias, 
        'series': series,           
        'fechas_reporte': [fecha.strftime('%Y-%m') for fecha in fechas_reporte],
        'trabajadores_series': trabajadores_series
    })
    
