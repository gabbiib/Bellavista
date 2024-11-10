from django.shortcuts import render
from django.db.models import Count
from django.http import JsonResponse
from gestion_reportes.models import Reportes_Problemas, Tareas, Asignacion
from gestion_datos.models import Usuarios, Problemas, Marcos
from django.db.models.functions import TruncMonth
from django.db.models import Q
from django.db.models import Count, Avg, F
import json
from datetime import datetime

def dashboard(request):
    # Obtener los datos de reportes
    incidentes = Reportes_Problemas.objects.all()

    # Obtener todos los trabajadores
    trabajadores_list = Usuarios.objects.all()

    # Obtener tipos de problemas con sus nombres e IDs
    tipo_incidentes = incidentes.values('tipo_incidente').annotate(count=Count('id'))
    tipos = []
    counts = []

    for tipo in tipo_incidentes:
        try:
            problema = Problemas.objects.get(id=tipo['tipo_incidente'])
            tipos.append({'id': problema.id, 'nombre': problema.nombre})
            counts.append(tipo['count'])
        except Problemas.DoesNotExist:
            tipos.append({'id': None, 'nombre': 'Desconocido'})
            counts.append(tipo['count'])

    # Obtener marcos únicos desde el modelo reportes_problemas y sus nombres e IDs
    marcos_ids = incidentes.values_list('marco', flat=True).distinct()
    marcos = []

    for marco_id in marcos_ids:
        try:
            marco = Marcos.objects.get(id=marco_id)
            marcos.append({'id': marco.id, 'nombre': marco.nombre})
        except Marcos.DoesNotExist:
            marcos.append({'id': None, 'nombre': 'Desconocido'})

    # Calcular el promedio de incidentes por mes
    num_meses = incidentes.dates('fecha_reporte', 'month').count()
    total_reportes = incidentes.count()
    promedio_reportes_por_mes = total_reportes / num_meses if num_meses > 0 else 0

    context = {
        'tipos': tipos,
        'counts': counts,
        'marcos': marcos,
        'trabajadores': trabajadores_list,
        'promedio_reportes_por_mes': promedio_reportes_por_mes,
    }

    # Verificar si la solicitud es AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Filtrar por tipo y marco si se recibe un request AJAX
        tipo_seleccionado = request.GET.get('tipo')
        marco_seleccionado = request.GET.get('marco')
        trabajador_seleccionado = request.GET.get('trabajador')
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')

        # Convertir a entero si no es 'Todos' o vacío
        if tipo_seleccionado:
            try:
                tipo_seleccionado = int(tipo_seleccionado)
                incidentes = incidentes.filter(tipo_incidente=tipo_seleccionado)
            except ValueError:
                pass

        if marco_seleccionado and marco_seleccionado != 'Todos':
            try:
                marco_seleccionado = int(marco_seleccionado)
                incidentes = incidentes.filter(marco=marco_seleccionado)
            except ValueError:
                pass

        if trabajador_seleccionado:
            incidentes = incidentes.filter(rut_usuario__rut=trabajador_seleccionado)

        if fecha_inicio and fecha_fin:
            incidentes = incidentes.filter(fecha_reporte__range=[fecha_inicio, fecha_fin])

        tipo_incidentes = incidentes.values('tipo_incidente').annotate(count=Count('id'))
        tipos = []
        counts = []

        for tipo in tipo_incidentes:
            try:
                problema = Problemas.objects.get(id=tipo['tipo_incidente'])
                tipos.append({'id': problema.id, 'nombre': problema.nombre})
                counts.append(tipo['count'])
            except Problemas.DoesNotExist:
                tipos.append({'id': None, 'nombre': 'Desconocido'})
                counts.append(tipo['count'])

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

    # Manejar el caso en el que no se proporcionen fechas
    if fecha_inicio and fecha_fin:
        reportes = reportes.filter(fecha_reporte__range=[fecha_inicio, fecha_fin])
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
    else:
        # Si no hay fechas proporcionadas, usar el rango completo de datos
        fecha_inicio = reportes.earliest('fecha_reporte').fecha_reporte
        fecha_fin = reportes.latest('fecha_reporte').fecha_reporte

    # Calcular el número de días entre las fechas
    delta_dias = (fecha_fin - fecha_inicio).days + 1  # +1 para incluir el día de inicio

    total_problemas = reportes.count()

    # Inicializar los promedios
    promedio_mensual = promedio_semanal = promedio_diario = 0

    # Calcular promedios
    if delta_dias > 0:
        dias = delta_dias
        promedio_diario = total_problemas / dias

        # Calcular promedio semanal si el rango es al menos una semana
        if delta_dias >= 7:
            semanas = dias / 7.0
            promedio_semanal = total_problemas / semanas

        # Calcular promedio mensual si el rango es al menos un mes
        if delta_dias >= 30:
            meses = dias / 30.44  # Promedio de días por mes
            promedio_mensual = total_problemas / meses

    kpi_data = {
        'total_problemas': total_problemas,
        'promedio_mensual': promedio_mensual,
        'promedio_semanal': promedio_semanal,
        'promedio_diario': promedio_diario
    }

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
        'trabajadores_series': trabajadores_series,
        'total_problemas': kpi_data['total_problemas'],
        'promedio_mensual': kpi_data['promedio_mensual'],
        'promedio_semanal': kpi_data['promedio_semanal'],
        'promedio_diario': kpi_data['promedio_diario']
    })



def obtener_promedio_problemas(request):
    # Calcula el total de problemas y el número de meses registrados
    total_problemas = Reportes_Problemas.objects.count()
    meses = Reportes_Problemas.objects.dates('fecha_reporte', 'month', order='ASC').count()
    
    # Si no hay datos, evitar la división por cero
    if meses == 0:
        promedio_mensual = 0
    else:
        promedio_mensual = total_problemas / meses

    return JsonResponse({
        'total_problemas': total_problemas,
        'meses': meses,
        'promedio_mensual': promedio_mensual
    })  

def inicio_admin(request):
    return render(request, 'inicio_admin.html')

###Benja
def reportes(request):
    trabajadores = Usuarios.objects.filter(rol__nombre='Usuario')
    return render(request, 'reportes.html', {'trabajadores': trabajadores})


def get_report_data(request):
    chart_type = request.GET.get('chartType')
    worker_id = request.GET.get('workerId')
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')

    data = Tareas.objects.all() 

    # Filtrar por trabajador si se selecciona uno
    if worker_id:
        data = data.filter(asignacion__trabajador__rut=worker_id)

    # Filtrar por rango de fechas
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