# roles/context_processors.py - Context processors para roles
from .models import PerfilUsuario

def user_role_context(request):
    """
    Context processor que agrega información del rol del usuario
    a todas las plantillas
    """
    context = {
        'user_area': None,
        'user_rol': None,
        'user_permisos': {},
        'can_access_admin': False,
    }
    
    if request.user.is_authenticated:
        try:
            perfil = request.user.perfil
            context.update({
                'user_area': perfil.area_trabajo,
                'user_rol': perfil.rol,
                'user_permisos': {
                    'puede_crear_proyectos': perfil.puede_crear_proyectos,
                    'puede_editar_proyectos': perfil.puede_editar_proyectos,
                    'puede_asignar_hilos': perfil.puede_asignar_hilos,
                    'puede_ver_dashboard': perfil.puede_ver_dashboard,
                    'puede_ver_mapa_mufas': perfil.puede_ver_mapa_mufas,
                    'puede_ver_analytics': perfil.puede_ver_analytics,
                    'es_supervisor': perfil.es_supervisor,
                },
                'can_access_admin': request.user.is_superuser,
            })
            
            # Agregar información específica del área
            area_codigo = perfil.area_trabajo.codigo
            context[f'is_{area_codigo}_user'] = True
            
            # Información del rol específico
            rol_codigo = perfil.rol.codigo
            context[f'is_{rol_codigo}'] = True
            
        except PerfilUsuario.DoesNotExist:
            # Usuario sin perfil - probablemente superuser o usuario de sistema
            context['can_access_admin'] = request.user.is_superuser
    
    return context