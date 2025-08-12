from django.contrib import admin
from .models import Mufa, Hilo, Conexion

# Inline para ver los hilos dentro de la Mufa (solo lectura para mejor rendimiento)
class HiloInline(admin.TabularInline):
    model = Hilo
    extra = 0
    can_delete = False
    show_change_link = True
    readonly_fields = ['numero', 'estado', 'uso', 'splitter', 'destino']
    fields = ['numero', 'estado', 'uso', 'splitter', 'destino']

@admin.register(Mufa)
class MufaAdmin(admin.ModelAdmin):
    inlines = [HiloInline]
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
