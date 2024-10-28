from django.shortcuts import render
from django.db.models import Count
from django.http import JsonResponse
from gestion_reportes.models import Reportes_Problemas
from gestion_datos.models import Usuarios

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


def inicio_admin(request):
    return render(request, 'inicio_admin.html')