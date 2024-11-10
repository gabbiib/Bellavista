from django.urls import path, include
from . import views

app_name = 'dashboards'

urlpatterns = [
    path('data/', include('gestion_datos.urls')),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('filtrar_reportes/', views.filtrar_reportes, name='filtrar_reportes'),
    path('reportes/datos/', views.get_report_data, name='get_report_data'), 
    path('reportes/', views.reportes, name='reportes'),
    path('kpi/', views.obtener_promedio_problemas, name='obtener_promedio_problemas')
]