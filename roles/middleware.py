# roles/middleware.py - Middleware para control de acceso por roles
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from .models import PerfilUsuario, RegistroAcceso

class RoleBasedAccessMiddleware:
    """
    Middleware que controla el acceso basado en roles y permisos del usuario
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs que requieren permisos específicos
        self.protected_urls = {
            # Proyectos - Creación
            'proyectos:create': 'puede_crear_proyectos',
            
            # Analytics
            'proyectos:analytics': 'puede_ver_analytics',
            
            # Mufas - Asignación de hilos
            'mufas:asignar_hilo': 'puede_asignar_hilos',
            
            # Mapa de mufas (algunos roles no deberían verlo)
            'mufas:mufas_json': 'puede_ver_mapa_mufas',
            'mufas:mapa': 'puede_ver_mapa_mufas',
        }

    def __call__(self, request):
        # Verificar permisos antes de procesar la vista
        if hasattr(request, 'resolver_match') and request.resolver_match:
            url_name = self.get_url_name(request.resolver_match)
            
            if url_name in self.protected_urls:
                required_permission = self.protected_urls[url_name]
                
                if not self.user_has_permission(request.user, required_permission):
                    return self.handle_access_denied(request, url_name)
        
        response = self.get_response(request)
        
        # Registrar acceso después de procesar la vista
        self.log_access(request, response)
        
        return response

    def get_url_name(self, resolver_match):
        """Obtener el nombre completo de la URL (namespace:name)"""
        if resolver_match.namespace:
            return f"{resolver_match.namespace}:{resolver_match.url_name}"
        return resolver_match.url_name

    def user_has_permission(self, user, permission):
        """Verificar si el usuario tiene el permiso específico"""
        if not user.is_authenticated:
            return False
        
        # Superusuarios siempre tienen acceso
        if user.is_superuser:
            return True
        
        # Verificar perfil de usuario
        try:
            perfil = user.perfil
            if not perfil.activo:
                return False
            
            # Verificar el permiso específico
            return getattr(perfil, permission, False)
            
        except PerfilUsuario.DoesNotExist:
            return False

    def handle_access_denied(self, request, url_name):
        """Manejar acceso denegado"""
        if request.user.is_authenticated:
            # Usuario autenticado pero sin permisos
            try:
                area = request.user.perfil.area_trabajo.nombre
                rol = request.user.perfil.rol.nombre
                message = f"Acceso denegado. Su rol '{rol}' del {area} no tiene permisos para esta función."
            except:
                message = "Acceso denegado. No tiene permisos para esta función."
            
            messages.error(request, message)
            return redirect('dashboard_home')
        else:
            # Usuario no autenticado
            messages.info(request, 'Debe iniciar sesión para acceder a esta función.')
            return redirect('admin:login')

    def log_access(self, request, response):
        """Registrar acceso del usuario"""
        if request.user.is_authenticated and hasattr(request, 'resolver_match'):
            try:
                # Solo registrar accesos a módulos principales
                if request.resolver_match and request.resolver_match.namespace in ['proyectos', 'mufas']:
                    modulo = request.resolver_match.namespace
                    accion = request.resolver_match.url_name
                    
                    # Obtener IP del cliente
                    ip = self.get_client_ip(request)
                    
                    RegistroAcceso.objects.create(
                        usuario=request.user,
                        accion=f"{accion} ({request.method})",
                        modulo=modulo,
                        ip_address=ip,
                        detalles=f"Status: {response.status_code}"
                    )
            except Exception:
                # No fallar si hay error en logging
                pass

    def get_client_ip(self, request):
        """Obtener IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RoleContextMiddleware:
    """
    Middleware que agrega información del rol al contexto de todas las plantillas
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Agregar información del usuario al request
        if request.user.is_authenticated:
            try:
                perfil = request.user.perfil
                request.user_area = perfil.area_trabajo
                request.user_rol = perfil.rol
                request.user_permisos = {
                    'puede_crear_proyectos': perfil.puede_crear_proyectos,
                    'puede_editar_proyectos': perfil.puede_editar_proyectos,
                    'puede_asignar_hilos': perfil.puede_asignar_hilos,
                    'puede_ver_dashboard': perfil.puede_ver_dashboard,
                    'puede_ver_mapa_mufas': perfil.puede_ver_mapa_mufas,
                    'puede_ver_analytics': perfil.puede_ver_analytics,
                    'es_supervisor': perfil.es_supervisor,
                }
            except PerfilUsuario.DoesNotExist:
                request.user_area = None
                request.user_rol = None
                request.user_permisos = {}
        
        response = self.get_response(request)
        return response