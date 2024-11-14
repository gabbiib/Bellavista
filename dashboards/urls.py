from django.urls import path, include
from . import views

app_name = 'dashboards'

urlpatterns = [
    path('data/', include('gestion_datos.urls')),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('filtrar_reportes/', views.filtrar_reportes, name='filtrar_reportes'),
    path('reportes/', views.reportes, name='reportes'),
    path('reportes/datos/', views.get_report_data, name='get_report_data'), 
    path('kpi/', views.obtener_promedio_problemas, name='obtener_promedio_problemas'),
    path("ubicaciones/", views.obtener_ubicaciones, name="obtener_ubicaciones"),
    path('mapa-reportes/', views.mapa_reportes, name='mapa_reportes'),
    path('api/trabajadores/', views.obtener_trabajadores, name='obtener_trabajadores'),
    path('api/marcos/', views.obtener_marcos, name='obtener_marcos'),
    path('api/tipo/', views.obtener_tipos_incidentes, name='obtener_tipos'),
    
]