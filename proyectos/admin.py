# proyectos/admin.py - Panel de Administración Avanzado (Solo Superusuarios)
from django.contrib import admin
from django.utils.html import format_html
from django.contrib.admin import AdminSite
from .models import Proyecto, SeguimientoProyecto, TareaProyecto

# Personalizar completamente el admin - Sin referencias a Django
admin.site.site_header = 'WinFibra - Centro de Control Administrativo'
admin.site.site_title = 'WinFibra Control Center'
admin.site.index_title = 'Panel de Gestión Empresarial'

# Personalizar texto de login
admin.site.login_template = 'admin/login_custom.html'

class SeguimientoInline(admin.TabularInline):
    model = SeguimientoProyecto
    extra = 0
    readonly_fields = ['fecha_registro', 'usuario']
    fields = [
        'fecha_registro', 'usuario', 'estado_anterior', 
        'estado_nuevo', 'progreso_anterior', 'progreso_nuevo', 
        'comentario'
    ]
    ordering = ['-fecha_registro']

class TareaInline(admin.TabularInline):
    model = TareaProyecto
    extra = 1
    fields = [
        'orden', 'nombre', 'estado', 'responsable', 
        'fecha_inicio', 'fecha_fin'
    ]
    ordering = ['orden']

@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    inlines = [TareaInline, SeguimientoInline]
    
    list_display = [
        'codigo', 'nombre_edificio', 'distrito', 'estado_badge',
        'prioridad_badge', 'progreso_bar', 'responsable',
        'dias_retraso_badge', 'presupuesto_status'
    ]
    
    list_filter = [
        'estado', 'prioridad', 'distrito', 'responsable',
        'fecha_creacion', 'fecha_actualizacion'
    ]
    
    search_fields = [
        'codigo', 'nombre_edificio', 'direccion', 'distrito'
    ]
    
    readonly_fields = [
        'dias_desde_inicio', 'dias_retraso', 'esta_retrasado',
        'presupuesto_restante', 'esta_sobre_presupuesto',
        'fecha_creacion', 'fecha_actualizacion'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'codigo', 'nombre_edificio', 'direccion',
                'departamento', 'distrito', 
                ('latitud', 'longitud'),
                ('cantidad_pisos', 'cantidad_departamentos')
            )
        }),
        ('Seguimiento del Proyecto', {
            'fields': (
                ('estado', 'prioridad', 'progreso_porcentaje'),
                ('fecha_inicio', 'fecha_fin_estimada', 'fecha_fin_real'),
                'responsable',
                'observaciones'
            )
        }),
        ('Presupuesto', {
            'fields': (
                ('presupuesto_estimado', 'presupuesto_gastado'),
                'presupuesto_restante', 'esta_sobre_presupuesto'
            )
        }),
        ('Información Automática', {
            'classes': ('collapse',),
            'fields': (
                ('fecha_creacion', 'fecha_actualizacion'),
                ('dias_desde_inicio', 'dias_retraso', 'esta_retrasado')
            )
        }),
    )
    
    def estado_badge(self, obj):
        color_map = {
            'planificacion': 'secondary',
            'aprobado': 'primary',
            'en_construccion': 'info',
            'paralizado': 'warning',
            'completado': 'success',
            'cancelado': 'danger'
        }
        color = color_map.get(obj.estado, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color, obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def prioridad_badge(self, obj):
        color_map = {
            'alta': 'danger',
            'media': 'warning', 
            'baja': 'success'
        }
        color = color_map.get(obj.prioridad, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color, obj.get_prioridad_display()
        )
    prioridad_badge.short_description = 'Prioridad'
    
    def progreso_bar(self, obj):
        if obj.progreso_porcentaje < 30:
            color = 'danger'
        elif obj.progreso_porcentaje < 70:
            color = 'warning'
        else:
            color = 'success'
            
        return format_html(
            '<div class="progress" style="height: 20px;">'
            '<div class="progress-bar bg-{}" style="width: {}%">'
            '{}%</div></div>',
            color, obj.progreso_porcentaje, obj.progreso_porcentaje
        )
    progreso_bar.short_description = 'Progreso'
    
    def dias_retraso_badge(self, obj):
        if obj.dias_retraso > 0:
            return format_html(
                '<span class="badge bg-danger">{} días</span>',
                obj.dias_retraso
            )
        return format_html('<span class="badge bg-success">En tiempo</span>')
    dias_retraso_badge.short_description = 'Retraso'
    
    def presupuesto_status(self, obj):
        if not obj.presupuesto_estimado:
            return format_html('<span class="text-muted">Sin presupuesto</span>')
        
        if obj.esta_sobre_presupuesto:
            return format_html(
                '<span class="badge bg-danger">Sobre presup.</span>'
            )
        
        porcentaje_usado = (obj.presupuesto_gastado / obj.presupuesto_estimado) * 100
        if porcentaje_usado > 80:
            color = 'warning'
        else:
            color = 'success'
            
        return format_html(
            '<span class="badge bg-{}">{:.1f}% usado</span>',
            color, porcentaje_usado
        )
    presupuesto_status.short_description = 'Presupuesto'


@admin.register(SeguimientoProyecto)
class SeguimientoProyectoAdmin(admin.ModelAdmin):
    list_display = [
        'proyecto', 'fecha_registro', 'usuario', 
        'estado_anterior', 'estado_nuevo', 
        'progreso_cambio', 'comentario_corto'
    ]
    
    list_filter = [
        'estado_nuevo', 'fecha_registro', 'usuario'
    ]
    
    search_fields = [
        'proyecto__codigo', 'proyecto__nombre_edificio', 'comentario'
    ]
    
    readonly_fields = ['fecha_registro']
    
    def progreso_cambio(self, obj):
        if obj.progreso_anterior is not None:
            cambio = obj.progreso_nuevo - obj.progreso_anterior
            if cambio > 0:
                return format_html(
                    '<span class="text-success">+{}%</span>', cambio
                )
            elif cambio < 0:
                return format_html(
                    '<span class="text-danger">{}%</span>', cambio
                )
            else:
                return format_html('<span class="text-muted">Sin cambio</span>')
        return f'{obj.progreso_nuevo}%'
    progreso_cambio.short_description = 'Cambio Progreso'
    
    def comentario_corto(self, obj):
        return obj.comentario[:50] + '...' if len(obj.comentario) > 50 else obj.comentario
    comentario_corto.short_description = 'Comentario'


@admin.register(TareaProyecto)
class TareaProyectoAdmin(admin.ModelAdmin):
    list_display = [
        'proyecto', 'orden', 'nombre', 'estado_badge',
        'responsable', 'fecha_fin', 'dias_para_vencer'
    ]
    
    list_filter = [
        'estado', 'proyecto', 'responsable'
    ]
    
    search_fields = [
        'nombre', 'descripcion', 'proyecto__codigo'
    ]
    
    ordering = ['proyecto', 'orden']
    
    def estado_badge(self, obj):
        color_map = {
            'pendiente': 'secondary',
            'en_progreso': 'info',
            'completada': 'success',
            'bloqueada': 'danger'
        }
        color = color_map.get(obj.estado, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color, obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def dias_para_vencer(self, obj):
        if obj.fecha_fin:
            from django.utils import timezone
            dias = (obj.fecha_fin - timezone.now().date()).days
            if dias < 0:
                return format_html(
                    '<span class="badge bg-danger">{} días atrasado</span>', abs(dias)
                )
            elif dias <= 3:
                return format_html(
                    '<span class="badge bg-warning">{} días</span>', dias
                )
            else:
                return format_html(
                    '<span class="badge bg-success">{} días</span>', dias
                )
        return '-'
    dias_para_vencer.short_description = 'Días para vencer'