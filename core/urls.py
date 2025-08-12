# core/urls.py - VERSIÓN CORREGIDA Y FUNCIONAL
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.urls import path, include
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, render
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.contrib.auth import views as auth_views

def redirect_to_dashboard(request):
    """Redireccionar página principal al dashboard"""
    return redirect('/dashboard/')

def dashboard_view(request):
    """Vista principal del dashboard"""
    # Valores simulados para demostración
    context = {
        'total_mufas': 2847,
        'hilos_disponibles': 18432,
        'proyectos_activos': 167,
        'ocupacion_promedio': 78.5,
        'demo': True
    }
    return render(request, 'dashboards/home.html', context)

def analytics_view(request):
    """Vista de analytics estático"""
    return render(request, 'demos/analytics_estatico.html', {'demo': True})

def api_overview(request):
    """API para datos generales del dashboard"""
    data = {
        'total_mufas': 2847,
        'hilos_disponibles': 18432,
        'proyectos_activos': 167,
        'ocupacion_promedio': 78.5,
        'roi_promedio': 184.5,
        'eficiencia_operativa': 87.2,
        'satisfaccion_cliente': 9.1,
        'alertas_criticas': 2,
        'timestamp': '2024-08-08T12:00:00Z'
    }
    return JsonResponse(data)

# 🌐 Personalización del Admin de WinFibra
admin.site.site_header = "🌐 WinFibra - Gestión de Fibra Óptica"
admin.site.site_title = "WinFibra Admin"
admin.site.index_title = "Panel de Control de Red"

urlpatterns = [
    # Página principal
    path('', redirect_to_dashboard, name='home'),
    
    # Sistema de autenticación
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Dashboard principal
    path('dashboard/', dashboard_view, name='dashboard_home'),
    path('analytics/', analytics_view, name='analytics_dashboard'),
    
    # APIs
    path('api/overview/', api_overview, name='api_overview'),
    
    # Demos estáticos
    path('demo/dashboard/', lambda request: render(request, 'demos/dashboard_estatico.html'), name='demo_dashboard'),
    path('demo/analytics/', lambda request: render(request, 'demos/analytics_estatico.html'), name='demo_analytics'),
    
    # Centro de Control Administrativo (solo superusuarios)
    path('admin/', admin.site.urls),
    path('control/', admin.site.urls),  # URL alternativa más profesional
    path('management/', admin.site.urls),  # URL alternativa para gestión
    
    # Módulos principales
    path('proyectos/', include('proyectos.urls')),
    path('mufas/', include('mufas.urls')),
    path('roles/', include('roles.urls')),
]

# Servir archivos estáticos en desarrollo y producción
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)