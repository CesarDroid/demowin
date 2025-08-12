# roles/admin.py - Administración de Roles y Perfiles
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import AreaTrabajo, RolUsuario, PerfilUsuario, RegistroAcceso

# Personalización del admin de usuarios
class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil del Usuario'
    fields = [
        'rol', 'telefono', 'dni', 'fecha_ingreso', 'activo',
        ('puede_ver_dashboard', 'puede_crear_proyectos', 'puede_editar_proyectos'),
        ('puede_asignar_hilos', 'puede_ver_mapa_mufas', 'puede_ver_analytics'),
    ]

class UserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)
    list_display = ['username', 'first_name', 'last_name', 'email', 'get_area', 'get_rol', 'is_active']
    list_filter = BaseUserAdmin.list_filter + ('perfil__rol__area',)
    
    def get_area(self, obj):
        if hasattr(obj, 'perfil'):
            return obj.perfil.area_trabajo.nombre
        return '-'
    get_area.short_description = 'Área'
    
    def get_rol(self, obj):
        if hasattr(obj, 'perfil'):
            color = {
                'comercial': 'primary',
                'planificacion': 'success', 
                'construccion': 'warning',
                'administracion': 'danger'
            }.get(obj.perfil.area_trabajo.codigo, 'secondary')
            
            return format_html(
                '<span class="badge bg-{}">{}</span>',
                color, obj.perfil.rol.nombre
            )
        return '-'
    get_rol.short_description = 'Rol'

# Re-registrar el UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(AreaTrabajo)
class AreaTrabajoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'activa', 'cantidad_roles']
    list_filter = ['activa']
    search_fields = ['nombre', 'codigo']
    
    def cantidad_roles(self, obj):
        return obj.roles.count()
    cantidad_roles.short_description = 'Cantidad de Roles'


@admin.register(RolUsuario) 
class RolUsuarioAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'area', 'cantidad_usuarios']
    list_filter = ['area']
    search_fields = ['nombre', 'codigo']
    filter_horizontal = ['permisos_especiales']
    
    def cantidad_usuarios(self, obj):
        count = obj.usuarios.count()
        if count > 0:
            return format_html(
                '<span class="badge bg-info">{} usuarios</span>',
                count
            )
        return 'Sin usuarios'
    cantidad_usuarios.short_description = 'Usuarios Asignados'


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = [
        'usuario', 'get_nombre_completo', 'rol', 'get_area', 
        'activo', 'es_supervisor', 'fecha_ingreso'
    ]
    list_filter = ['rol__area', 'rol', 'activo', 'fecha_ingreso']
    search_fields = ['usuario__username', 'usuario__first_name', 'usuario__last_name', 'dni']
    readonly_fields = ['es_supervisor', 'puede_supervisar_area']
    
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('usuario', 'rol', 'activo')
        }),
        ('Datos Personales', {
            'fields': ('telefono', 'dni', 'fecha_ingreso')
        }),
        ('Permisos de Interfaz', {
            'fields': (
                ('puede_ver_dashboard', 'puede_crear_proyectos'),
                ('puede_editar_proyectos', 'puede_asignar_hilos'),
                ('puede_ver_mapa_mufas', 'puede_ver_analytics'),
            )
        }),
        ('Información Automática', {
            'classes': ('collapse',),
            'fields': ('es_supervisor', 'puede_supervisar_area')
        }),
    )
    
    def get_nombre_completo(self, obj):
        return obj.usuario.get_full_name() or obj.usuario.username
    get_nombre_completo.short_description = 'Nombre'
    
    def get_area(self, obj):
        return obj.area_trabajo.nombre
    get_area.short_description = 'Área'


@admin.register(RegistroAcceso)
class RegistroAccesoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'accion', 'modulo', 'fecha_hora', 'ip_address']
    list_filter = ['modulo', 'fecha_hora', 'usuario']
    search_fields = ['usuario__username', 'accion', 'modulo']
    readonly_fields = ['fecha_hora']
    date_hierarchy = 'fecha_hora'
    
    def has_add_permission(self, request):
        return False  # No permitir agregar manualmente
    
    def has_change_permission(self, request, obj=None):
        return False  # Solo lectura