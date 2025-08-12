# proyectos/urls.py - VERSIÓN CORREGIDA
from django.urls import path
from . import views

app_name = "proyectos"

urlpatterns = [
    # Dashboard principal de proyectos
    path('', views.proyecto_dashboard_view, name='dashboard'),
    
    # Listado de proyectos
    path('lista/', views.ProyectoListView.as_view(), name='list'),
    
    # Crear nuevo proyecto
    path('crear/', views.CrearProyectoView.as_view(), name='create'),
    
    # Analytics de proyectos
    path('analytics/', views.ProyectoAnalyticsView.as_view(), name='analytics'),
]