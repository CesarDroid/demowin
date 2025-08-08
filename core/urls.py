from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect, render
from django.conf import settings
from django.conf.urls.static import static

def redirect_to_dashboard(request):
    return redirect('/dashboard/')

def dashboard_view(request):
    return render(request, 'dashboards/home.html', {'demo': True})

def analytics_view(request):
    return render(request, 'demos/analytics_estatico.html', {'demo': True})

urlpatterns = [
    # Página principal
    path('', redirect_to_dashboard, name='home'),
    
    # Dashboard básico
    path('dashboard/', dashboard_view, name='dashboard_home'),
    path('analytics/', analytics_view, name='analytics_dashboard'),
    
    # Demos estáticos
    path('demo/dashboard/', lambda request: render(request, 'demos/dashboard_estatico.html'), name='demo_dashboard'),
    path('demo/analytics/', lambda request: render(request, 'demos/analytics_estatico.html'), name='demo_analytics'),
    
    # Panel de administración
    path('admin/', admin.site.urls),
    
    # Módulos
    path('proyectos/', include('proyectos.urls', namespace='proyectos')),
    path('mufas/', include('mufas.urls', namespace='mufas')),
    path('roles/', include('roles.urls', namespace='roles')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)