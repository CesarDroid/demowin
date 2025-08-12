# core/middleware.py - Middleware para seguridad del admin
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
import re

class AdminSuperuserOnlyMiddleware:
    """
    Middleware que restringe el acceso al admin solo a superusuarios
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Patrón para detectar URLs del admin (excluir archivos estáticos del admin)
        self.admin_url_pattern = re.compile(r'^/admin/(?!jsi18n|static/)')

    def __call__(self, request):
        # Verificar si es una URL del admin (excluyendo archivos estáticos)
        if self.admin_url_pattern.match(request.path):
            # Permitir acceso solo si el usuario está autenticado Y es superusuario
            if not request.user.is_authenticated:
                # Redirigir al login del admin
                return redirect('/admin/login/')
            elif not request.user.is_superuser:
                # Usuario normal intentando acceder al admin
                messages.error(
                    request, 
                    'Acceso denegado. El panel de administración está restringido a superusuarios.'
                )
                return redirect('dashboard_home')
        
        response = self.get_response(request)
        return response