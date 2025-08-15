from django.contrib import admin
from .models import Mufa, Hilo, Conexion, CableSlot, CableTroncal, CableDerivacion

# Inline para ver los hilos dentro de la Mufa (solo lectura para mejor rendimiento)
class HiloInline(admin.TabularInline):
    model = Hilo
    extra = 0
    can_delete = False
    show_change_link = True
    readonly_fields = ['numero', 'estado', 'uso', 'splitter', 'destino']
    fields = ['numero', 'estado', 'uso', 'splitter', 'destino']

# Inline para ver los slots de cables dentro de la Mufa
class CableSlotInline(admin.TabularInline):
    model = CableSlot
    extra = 1
    fields = ['numero_slot', 'tipo_cable', 'cable_troncal', 'estado', 'hilos_utilizados', 'descripcion']

# Inline para mostrar cables de derivación en las mufas
class CableDerivacionInline(admin.TabularInline):
    model = CableDerivacion
    fk_name = 'mufa_origen'
    extra = 0
    fields = ['codigo', 'nombre_destino', 'tipo_destino', 'slot_origen', 'estado', 'capacidad', 'cliente']
    readonly_fields = []
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('slot_origen', 'proyecto')

@admin.register(Mufa)
class MufaAdmin(admin.ModelAdmin):
    inlines = [HiloInline, CableSlotInline, CableDerivacionInline]
    list_display = [
        'codigo', 'tipo', 'cable_troncal', 'ubicacion',
        'descripcion', 'latitud', 'longitud',
        'capacidad_hilos', 'distrito', 'total_hilos'
    ]
    fields = [
        'tipo', 'cable_troncal', 'codigo', 'descripcion',
        'ubicacion', 'latitud', 'longitud',
        'capacidad_hilos', 'distrito'
    ]
    readonly_fields = ['distrito']

    def total_hilos(self, obj):
        return obj.hilos.count()
    total_hilos.short_description = 'Cantidad de Hilos'

# Admin para Hilo, con inline de Conexiones
class ConexionInline(admin.TabularInline):
    model = Conexion
    fk_name = 'origen'
    extra = 0
    fields = ['destino', 'get_mufa_destino', 'observaciones']
    readonly_fields = ['get_mufa_destino']

    def get_mufa_destino(self, obj):
        return obj.destino.mufa.codigo if obj.destino else ''
    get_mufa_destino.short_description = 'Mufa Destino'

@admin.register(Hilo)
class HiloAdmin(admin.ModelAdmin):
    inlines = [ConexionInline]
    list_display = ['numero', 'mufa', 'estado', 'uso', 'splitter', 'destino']
    list_filter = ['estado', 'splitter', 'mufa__codigo']
    search_fields = ['numero', 'uso', 'destino', 'mufa__codigo']

@admin.register(Conexion)
class ConexionAdmin(admin.ModelAdmin):
    list_display = ['origen', 'destino', 'get_mufa_origen', 'get_mufa_destino']

    def get_mufa_origen(self, obj):
        return obj.origen.mufa.codigo
    get_mufa_origen.short_description = 'Mufa Origen'

    def get_mufa_destino(self, obj):
        return obj.destino.mufa.codigo
    get_mufa_destino.short_description = 'Mufa Destino'


@admin.register(CableSlot)
class CableSlotAdmin(admin.ModelAdmin):
    list_display = ['mufa', 'numero_slot', 'tipo_cable', 'cable_troncal', 'estado', 'hilos_utilizados', 'porcentaje_utilizacion']
    list_filter = ['tipo_cable', 'estado', 'mufa__distrito', 'cable_troncal']
    search_fields = ['mufa__codigo', 'descripcion', 'cable_troncal__codigo']
    ordering = ['mufa__codigo', 'numero_slot']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('mufa', 'numero_slot', 'tipo_cable', 'estado')
        }),
        ('Cable y Capacidad', {
            'fields': ('cable_troncal', 'hilos_utilizados', 'descripcion')
        }),
        ('Fechas', {
            'fields': ('fecha_instalacion',),
            'classes': ('collapse',)
        }),
    )


@admin.register(CableTroncal)
class CableTroncalAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'capacidad', 'get_capacidad_display', 'descripcion', 'total_mufas_conectadas']
    list_filter = ['capacidad']
    search_fields = ['codigo', 'descripcion']
    ordering = ['codigo']
    
    def total_mufas_conectadas(self, obj):
        return obj.mufas.count()
    total_mufas_conectadas.short_description = 'Mufas Conectadas'


@admin.register(CableDerivacion)
class CableDerivacionAdmin(admin.ModelAdmin):
    list_display = [
        'codigo', 'mufa_origen', 'nombre_destino', 'tipo_destino', 
        'estado', 'capacidad', 'cliente', 'fecha_instalacion'
    ]
    
    list_filter = [
        'estado', 'tipo_destino', 'capacidad', 'mufa_origen__distrito',
        'fecha_instalacion', 'fecha_creacion'
    ]
    
    search_fields = [
        'codigo', 'nombre_destino', 'direccion_destino', 'cliente', 
        'numero_contrato', 'mufa_origen__codigo'
    ]
    
    ordering = ['codigo']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'mufa_origen', 'slot_origen', 'estado')
        }),
        ('Destino', {
            'fields': (
                'nombre_destino', 'tipo_destino', 'direccion_destino',
                ('latitud_destino', 'longitud_destino')
            )
        }),
        ('Características Técnicas', {
            'fields': ('capacidad', 'longitud_metros')
        }),
        ('Información Comercial', {
            'fields': ('cliente', 'numero_contrato', 'proyecto'),
            'classes': ('collapse',)
        }),
        ('Instalación', {
            'fields': ('fecha_instalacion', 'tecnico_instalador'),
            'classes': ('collapse',)
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        }),
        ('Información del Sistema', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',),
            'description': 'Información automática del sistema'
        })
    )
    
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'mufa_origen', 'slot_origen', 'proyecto'
        )
    
    def save_model(self, request, obj, form, change):
        """
        Personalizar el guardado para actualizar el slot automáticamente.
        """
        super().save_model(request, obj, form, change)
        
        # Mensaje informativo si se asignó automáticamente un slot
        if obj.slot_origen and hasattr(obj, '_slot_auto_updated'):
            self.message_user(
                request, 
                f'El slot {obj.slot_origen} fue marcado automáticamente como ocupado.',
                level='INFO'
            )


