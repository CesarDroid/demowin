# proyectos/urls.py - CON DASHBOARD
from django.urls import path
from .views import (
    ProyectoListView, 
    CrearProyectoView, 
    DashboardProyectosView,
    ProyectoDetalleView
)

app_name = "proyectos"

urlpatterns = [
    # Dashboard principal - nueva página de inicio
    path("", DashboardProyectosView.as_view(), name="dashboard"),
    
    # Lista completa de proyectos
    path("lista/", ProyectoListView.as_view(), name="list"),
    
    # Crear proyecto
    path("crear/", CrearProyectoView.as_view(), name="create"),
    
    # Ver detalle de proyecto
    path("detalle/<int:pk>/", ProyectoDetalleView.as_view(), name="detail"),
]