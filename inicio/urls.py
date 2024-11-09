from django.urls import path, include
from . import views  
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

app_name = 'inicio'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('inicio_admin/', views.inicio_admin, name='inicio_admin'),
    path('trabajador/', views.trabajador, name='trabajador'),
    path('editar_perfil/', views.editar_perfil, name='editar_perfil'),  
    path('recuperar_contrasena/', views.recuperar_contrasena, name='recuperar_contrasena'),  
    path('contacto/', views.contacto, name='contacto'), 
    path('nosotros/', views.nosotros, name='nosotros'), 
    path('login/', views.login_view, name='login'), 
    path('logout/', views.logout_view, name='logout'),
    path('administrador/', views.administrador, name='administrador'),  
    path('enviar_enlace/', views.enviar_enlace_view, name='enviar_enlace'),  
    path('recuperar_contrasena/codigo/<str:codigo>/', views.recuperar_contrasena_codigo, name='recuperar_contrasena_codigo'),  
    path('contactar_admin/', views.contactar_admin_view, name='contactar_admin'),  
    path('recuperar_contrasena/enviar_enlace/', views.enviar_enlace_view, name='enviar_enlace'),
    path('recuperar_contrasena/contactar_admin/', views.contactar_admin_view, name='contactar_admin'),
    path('recuperar_contrasena/', views.enviar_enlace_view, name='recuperar_contrasena'),
    path('recuperar-contrasena/<str:codigo>/', views.recuperar_contrasena_codigo, name='recuperar_contrasena_codigo'),
    path('actualizar_tarea/<int:tarea_id>/', views.actualizar_tarea, name='actualizar_tarea'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
