from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add_info.html/', views.add_page, name='add_page'),
    path('perform_delete/', views.perform_delete, name='perform_delete'),
    path('delete_page/', views.delete_page, name='delete_page'),
    path('edit_info/', views.edit_page, name='edit_page'),
    path('success_add/', views.perform_add, name='perform_add'),
    path('getUserData/', views.get_user_data, name='get_user_data'),
    path('success_delete/', views.success_delete, name='success_delete'),
    path('getNames/', views.get_names, name='get_names'),
    path('success_edit/', views.success_edit, name='success_edit'),
    path('editData/', views.edit_data, name='edit_data'),
    path('get_usuarios/', views.get_usuarios, name='get_usuarios'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('filtrar_reportes/', views.filtrar_reportes, name='filtrar_reportes'),
    ]

