from django.urls import path, include
from . import views  
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from .views import ver_reportes, editar_reporte 

app_name = 'gestion_usuarios'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('login/', views.login_view, name='login'), 
    path('reporte/', views.reporte_view, name='reporte'),
    path('trabajador/', views.trabajador, name='trabajador'),
    path('editar_perfil/', views.editar_perfil, name='editar_perfil'), 
    path('logout/', views.logout_view, name='logout'),
    path('reporte_exito/', views.reporte_exito, name='reporte_exito'),
    path('contacto/', views.contacto, name='contacto'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('recuperar_contrasena/enviar_enlace/', views.enviar_enlace_view, name='enviar_enlace'),
    path('recuperar_contrasena/contactar_admin/', views.contactar_admin_view, name='contactar_admin'),
    path('recuperar_contrasena/', views.enviar_enlace_view, name='recuperar_contrasena'),
    path('recuperar-contrasena/<str:codigo>/', views.recuperar_contrasena_codigo, name='recuperar_contrasena_codigo'),
    path('administrador/', views.administrador, name='administrador'), 
    path('reportes/', ver_reportes, name='ver_reportes'),
    path('ver-imagen/<int:reporte_id>/', views.ver_imagen, name='ver_imagen'),
    path('reportes/editar/<int:id>/', editar_reporte, name='editar_reporte'),
    path('guardar_reportes/', views.ver_reportes, name='guardar_reportes'),
    path('actualizar_tarea/<int:tarea_id>/', views.actualizar_tarea, name='actualizar_tarea'),
    path('inicioadmin/', views.index, name='inicioadmin'),
    path('add_info.html/', views.add_page, name='add_page'),
    path('perform_delete/', views.perform_delete, name='perform_delete'),
    path('delete_page/', views.delete_page, name='delete_page'),
    path('edit_info.html/', views.edit_page, name='edit_page'),
    path('success_add/', views.perform_add, name='perform_add'),
    path('getUserData/', views.get_user_data, name='get_user_data'),
    path('success_delete/', views.success_delete, name='success_delete'),
    path('getNames/', views.get_names, name='get_names'),
    path('success_edit/', views.success_edit, name='success_edit'),
    path('editData/', views.edit_data, name='edit_data'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('filtrar_reportes/', views.filtrar_reportes, name='filtrar_reportes'),
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
    path('gestion_usuarios/', views.gestion_usuarios, name='gestion_usuarios'),
    path('eliminar_usuario/', views.eliminar_usuario, name='eliminar_usuario'),
    path('editar_usuario/', views.editar_usuario, name='editar_usuario'),
    path('crear_usuario/', views.crear_usuario, name='crear_usuario'),
    path('inicio_admin/', views.inicio_admin, name='inicio_admin'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)