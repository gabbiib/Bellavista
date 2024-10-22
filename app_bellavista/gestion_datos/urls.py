from django.urls import path, include
from . import views

app_name = 'gestion_datos'

urlpatterns = [
    path('gestion_usuario/', views.gestion_usuario, name='gestion_usuario'),
    path('registrarUsuario/', views.registrarUsuario, name='registrar_usuario'),
    path('edicionUsuario/<str:rut>/', views.edicionUsuario, name='edicion_usuario'),
    path('eliminarUsuario/<str:rut>/', views.eliminarUsuario, name='eliminar_usuario'),
    path('gestion_problema/', views.gestion_problema, name='gestion_problema'),
    path('registrarProblema/', views.registrarProblema, name='registrar_problema'),
    path('edicionProblema/<str:id>/', views.edicionProblema, name='edicion_problema'),
    path('eliminarProblema/<str:id>/', views.eliminarProblema, name='eliminar_problema'),
    path('gestion_marco/', views.gestion_marcos, name='gestion_marco'),
    path('registrarMarco/', views.registrarMarco, name='registrar_marco'),
    path('edicionMarco/<str:id>/', views.edicionMarco, name='edicion_marco'),
    path('eliminarMarco/<str:id>/', views.eliminarMarco, name='eliminar_marco'),
    path('usuarios/', include('gestion_usuarios.urls')),
]

