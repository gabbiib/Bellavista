from django.urls import path, include
from . import views  
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from .views import ver_reportes, editar_reporte 

app_name = 'gestion_reportes'

urlpatterns = [
    path('reporte/', views.reporte_view, name='reporte'),
    path('reporte_exito/', views.reporte_exito, name='reporte_exito'),
    path('reportes/', ver_reportes, name='ver_reportes'),
    path('ver-imagen/<int:reporte_id>/', views.ver_imagen, name='ver_imagen'),
    path('reportes/editar/<int:id>/', editar_reporte, name='editar_reporte'),
    path('guardar_reportes/', views.ver_reportes, name='guardar_reportes'),
    path('actualizar_tarea/<int:tarea_id>/', views.actualizar_tarea, name='actualizar_tarea'),
    path('tareas/', views.lista_tareas, name='lista_tareas'),
    path('reportes_tareas/', views.reportes_tareas, name='reportes_tareas'),
    path('reportes_tareas/datos/', views.get_report_data, name='get_report_data'), 
    path('asignar-tarea/', views.asignar_tarea_ajax, name='asignar_tarea_ajax'),
    path('eliminar-asignacion/', views.eliminar_asignacion_ajax, name='eliminar_asignacion_ajax'),
    path('editar-asignacion/', views.editar_asignacion_ajax, name='editar_asignacion_ajax'),
    path('eliminar-tarea/', views.eliminar_tarea_ajax, name='eliminar_tarea_ajax'),
    path('editar-tarea/', views.editar_tarea_ajax, name='editar_tarea_ajax'),
    path('obtener-tabla-asignaciones/', views.obtener_tabla_asignaciones, name='obtener_tabla_asignaciones'),
    path('obtener-tabla-tareas/', views.obtener_tabla_tareas, name='obtener_tabla_tareas'),
    path('filtrar_tareas/', views.filtrar_tareas_ajax, name='filtrar_tareas_ajax'),
    path('crear_tarea/', views.crear_tarea_ajax, name='crear_tarea_ajax'),
    path('obtener-reportes-problemas-disponibles/', views.obtener_reportes_problemas_disponibles, name='obtener_reportes_problemas_disponibles'),
    #path('crearTarea',views.crearTareaView.as_view(),name='CrearTareaN')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)