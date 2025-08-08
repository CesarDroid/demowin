# ASEGURAR QUE ESTOS IMPORTS ESTÉN AL INICIO DEL ARCHIVO:
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, TemplateView  # ← AGREGAR TemplateView aquí
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# TUS IMPORTS DE MODELOS Y FORMS (mantener los existentes)
from .models import Proyecto, SeguimientoProyecto, TareaProyecto
from .forms import ProyectoForm

# AGREGAR esta nueva vista al final del archivo existente
@method_decorator(login_required, name='dispatch')
class ProyectoAnalyticsView(TemplateView):
    """Vista de analytics específica para proyectos"""
    template_name = 'proyectos/analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Agregar métricas específicas de proyectos
        context.update({
            'proyectos_analytics': True,
            'roi_promedio': 184.5,
            'eficiencia_promedio': 87.2,
        })
        
        return context