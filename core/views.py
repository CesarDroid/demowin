# core/views.py - VERSIÓN SIMPLIFICADA PARA EMPEZAR

from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse

# Importar modelos
try:
    from mufas.models import Mufa, Hilo
    from proyectos.models import Proyecto
except ImportError:
    # Si hay problemas de importación, usar valores por defecto
    Mufa = None
    Hilo = None
    Proyecto = None

class DashboardHomeView(TemplateView):
    template_name = 'dashboards/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas básicas (con manejo de errores)
        try:
            if Mufa:
                total_mufas = Mufa.objects.count()
                mufas_operativas = Mufa.objects.filter(estado='operativa').count() if hasattr(Mufa.objects.first(), 'estado') else total_mufas
            else:
                total_mufas = 0
                mufas_operativas = 0
                
            if Hilo:
                hilos_libres = Hilo.objects.filter(estado='libre').count()
                hilos_ocupados = Hilo.objects.filter(estado='ocupado').count()
            else:
                hilos_libres = 0
                hilos_ocupados = 0
                
            if Proyecto:
                proyectos_activos = Proyecto.objects.filter(
                    estado__in=['planificacion', 'aprobado', 'en_construccion']
                ).count()
            else:
                proyectos_activos = 0
                
            # Calcular ocupación promedio
            total_hilos = hilos_libres + hilos_ocupados
            ocupacion_promedio = round((hilos_ocupados / total_hilos * 100) if total_hilos > 0 else 0, 1)
            
        except Exception as e:
            # Valores por defecto si hay error
            print(f"Error obteniendo estadísticas: {e}")
            total_mufas = 0
            mufas_operativas = 0
            hilos_libres = 0
            hilos_ocupados = 0
            proyectos_activos = 0
            ocupacion_promedio = 0
        
        context.update({
            'total_mufas': total_mufas,
            'mufas_operativas': mufas_operativas,
            'hilos_libres': hilos_libres,
            'hilos_ocupados': hilos_ocupados,
            'proyectos_activos': proyectos_activos,
            'ocupacion_promedio': ocupacion_promedio,
            'sistema_operativo': True,
            'alertas': [],  # Sin alertas por ahora
            'proyectos_criticos': 0,
        })
        
        return context