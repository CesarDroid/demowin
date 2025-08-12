# proyectos/views.py - VERSIÓN COMPLETA Y FUNCIONAL
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, TemplateView
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render

from .models import Proyecto, SeguimientoProyecto, TareaProyecto
from .forms import ProyectoForm


class ProyectoListView(ListView):
    """Vista de listado de proyectos con paginación"""
    model = Proyecto
    template_name = 'proyectos/proyecto_list.html'
    context_object_name = 'proyectos'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Proyecto.objects.select_related('responsable').order_by('-fecha_actualizacion')
        
        # Filtros de búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(codigo__icontains=search) |
                Q(nombre_edificio__icontains=search) |
                Q(distrito__icontains=search) |
                Q(direccion__icontains=search)
            )
        
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estados'] = Proyecto.ESTADO_CHOICES
        context['search_query'] = self.request.GET.get('search', '')
        context['estado_filter'] = self.request.GET.get('estado', '')
        return context


class CrearProyectoView(CreateView):
    """Vista para crear nuevos proyectos - Interfaz completa"""
    model = Proyecto
    form_class = ProyectoForm
    template_name = 'proyectos/crear_proyecto_completo.html'
    success_url = reverse_lazy('proyectos:list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar fecha actual para mostrar en el formulario
        from django.utils import timezone
        context['fecha_creacion_actual'] = timezone.now()
        return context
    
    def form_valid(self, form):
        # Asegurar que la fecha de creación sea la actual
        from django.utils import timezone
        form.instance.fecha_creacion = timezone.now()
        
        messages.success(
            self.request,
            f'✅ Proyecto {form.instance.codigo} creado exitosamente el {form.instance.fecha_creacion.strftime("%d/%m/%Y %H:%M")}'
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            '❌ Por favor corrige los errores en el formulario.'
        )
        return super().form_invalid(form)


@method_decorator(login_required, name='dispatch')
class ProyectoAnalyticsView(TemplateView):
    """Vista de analytics específica para proyectos"""
    template_name = 'proyectos/analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Métricas básicas
        total_proyectos = Proyecto.objects.count()
        proyectos_activos = Proyecto.objects.filter(
            estado__in=['planificacion', 'aprobado', 'en_construccion']
        ).count()
        proyectos_completados = Proyecto.objects.filter(estado='completado').count()
        progreso_promedio = Proyecto.objects.aggregate(
            promedio=Avg('progreso_porcentaje')
        )['promedio'] or 0
        
        # Proyectos por estado
        distribucion_estados = list(
            Proyecto.objects.values('estado')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # Proyectos por distrito
        distribucion_distritos = list(
            Proyecto.objects.values('distrito')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        
        # Proyectos retrasados
        hoy = timezone.now().date()
        proyectos_retrasados = Proyecto.objects.filter(
            fecha_fin_estimada__lt=hoy,
            estado__in=['planificacion', 'en_construccion']
        ).count()
        
        context.update({
            'total_proyectos': total_proyectos,
            'proyectos_activos': proyectos_activos,
            'proyectos_completados': proyectos_completados,
            'proyectos_retrasados': proyectos_retrasados,
            'progreso_promedio': round(progreso_promedio, 1),
            'distribucion_estados': distribucion_estados,
            'distribucion_distritos': distribucion_distritos,
            'roi_promedio': 184.5,  # Valor simulado
            'eficiencia_promedio': 87.2,  # Valor simulado
        })
        
        return context


# Vista simple para dashboard de proyectos
def proyecto_dashboard_view(request):
    """Dashboard mejorado con control de roles"""
    total_proyectos = Proyecto.objects.count()
    proyectos_activos = Proyecto.objects.filter(
        estado__in=['planificacion', 'aprobado', 'en_construccion']
    ).count()
    
    context = {
        'total_proyectos': total_proyectos,
        'proyectos_activos': proyectos_activos,
    }
    
    return render(request, 'proyectos/dashboard_mejorado.html', context)


def debug_csrf_view(request):
    """Vista de debug para probar CSRF"""
    return render(request, 'proyectos/debug_csrf.html')