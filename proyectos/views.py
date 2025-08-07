# proyectos/views.py - CON DASHBOARD
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, TemplateView
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.utils import timezone
from .models import Proyecto, SeguimientoProyecto, TareaProyecto
from .forms import ProyectoForm

class ProyectoListView(ListView):
    model = Proyecto
    template_name = 'proyectos/proyecto_list.html'
    context_object_name = 'proyectos'
    paginate_by = 20

class CrearProyectoView(CreateView):
    model = Proyecto
    form_class = ProyectoForm
    template_name = "proyectos/crear_proyecto.html"
    success_url = reverse_lazy("proyectos:list")
    
    def form_valid(self, form):
        messages.success(self.request, 'Proyecto creado exitosamente!')
        return super().form_valid(form)


class DashboardProyectosView(TemplateView):
    template_name = 'proyectos/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # === ESTADÍSTICAS GENERALES ===
        total_proyectos = Proyecto.objects.count()
        proyectos_activos = Proyecto.objects.filter(
            estado__in=['planificacion', 'aprobado', 'en_construccion']
        ).count()
        
        proyectos_paralizados = Proyecto.objects.filter(estado='paralizado')
        proyectos_retrasados = [p for p in Proyecto.objects.all() if p.esta_retrasado]
        proyectos_sobre_presupuesto = [p for p in Proyecto.objects.all() if p.esta_sobre_presupuesto]
        
        # === DISTRIBUCIÓN POR ESTADO ===
        estados_stats = Proyecto.objects.values('estado').annotate(
            cantidad=Count('id')
        ).order_by('-cantidad')
        
        # === PROYECTOS POR PRIORIDAD ===
        prioridad_stats = Proyecto.objects.values('prioridad').annotate(
            cantidad=Count('id')
        ).order_by('-cantidad')
        
        # === PROGRESO PROMEDIO ===
        progreso_promedio = Proyecto.objects.filter(
            estado__in=['en_construccion', 'completado']
        ).aggregate(promedio=Avg('progreso_porcentaje'))['promedio'] or 0
        
        # === PROYECTOS QUE NECESITAN ATENCIÓN ===
        proyectos_criticos = Proyecto.objects.filter(
            Q(estado='paralizado') | 
            Q(prioridad='alta', progreso_porcentaje__lt=50) |
            Q(fecha_fin_estimada__lt=timezone.now().date(), estado__in=['planificacion', 'en_construccion'])
        ).order_by('prioridad', 'fecha_fin_estimada')[:10]
        
        # === ACTIVIDAD RECIENTE ===
        actividad_reciente = SeguimientoProyecto.objects.select_related(
            'proyecto', 'usuario'
        ).order_by('-fecha_registro')[:10]
        
        # === TAREAS PENDIENTES ===
        tareas_pendientes = TareaProyecto.objects.filter(
            estado__in=['pendiente', 'bloqueada']
        ).select_related('proyecto').order_by('fecha_fin')[:10]
        
        context.update({
            # Estadísticas generales
            'total_proyectos': total_proyectos,
            'proyectos_activos': proyectos_activos,
            'proyectos_paralizados_count': proyectos_paralizados.count(),
            'proyectos_retrasados_count': len(proyectos_retrasados),
            'proyectos_sobre_presupuesto_count': len(proyectos_sobre_presupuesto),
            'progreso_promedio': round(progreso_promedio, 1),
            
            # Listas detalladas
            'proyectos_paralizados': proyectos_paralizados,
            'proyectos_retrasados': proyectos_retrasados[:10],
            'proyectos_sobre_presupuesto': proyectos_sobre_presupuesto[:10],
            'proyectos_criticos': proyectos_criticos,
            
            # Distribuciones
            'estados_stats': estados_stats,
            'prioridad_stats': prioridad_stats,
            
            # Actividad
            'actividad_reciente': actividad_reciente,
            'tareas_pendientes': tareas_pendientes,
        })
        
        return context


class ProyectoDetalleView(TemplateView):
    template_name = 'proyectos/proyecto_detalle.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proyecto_id = kwargs.get('pk')
        
        proyecto = Proyecto.objects.get(id=proyecto_id)
        seguimientos = proyecto.seguimientos.select_related('usuario')[:20]
        tareas = proyecto.tareas.select_related('responsable').order_by('orden')
        
        context.update({
            'proyecto': proyecto,
            'seguimientos': seguimientos,
            'tareas': tareas,
        })
        
        return context