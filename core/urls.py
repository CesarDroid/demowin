# core/urls.py - ACTUALIZADO PARA INCLUIR DASHBOARD

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from .views import DashboardHomeView

def redirect_to_dashboard(request):
    """Redirige la página principal al dashboard"""
    return redirect('dashboard_home')

urlpatterns = [
    # Página principal - redirige al dashboard
    path('', redirect_to_dashboard, name='home'),
    
    # Dashboard principal
    path('dashboard/', DashboardHomeView.as_view(), name='dashboard_home'),
    
    # Panel de administración
    path('admin/', admin.site.urls),
    
    # Módulo de mufas (mapa, JSON, asignaciones)
    path('mufas/', include('mufas.urls', namespace='mufas')),
    
    # Módulo de proyectos (dashboard, creación, listado)
    path('proyectos/', include('proyectos.urls', namespace='proyectos')),
    
    # Módulo de roles/permisos
    path('roles/', include('roles.urls', namespace='roles')),
]

# Configuración para archivos estáticos en desarrollo
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)