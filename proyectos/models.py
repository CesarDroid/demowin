# proyectos/models.py - VERSIÓN EXTENDIDA
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Proyecto(models.Model):
    # Campos existentes
    codigo               = models.CharField(max_length=100, unique=True)
    nombre_edificio      = models.CharField(max_length=255)
    direccion            = models.CharField(max_length=255)
    departamento         = models.CharField(max_length=255)
    distrito             = models.CharField(max_length=100)
    latitud              = models.FloatField(blank=True, null=True)
    longitud             = models.FloatField(blank=True, null=True)
    cantidad_pisos       = models.PositiveIntegerField()
    cantidad_departamentos = models.PositiveIntegerField()
    
    # NUEVOS CAMPOS PARA SEGUIMIENTO
    ESTADO_CHOICES = [
        ('planificacion', '📋 Planificación'),
        ('aprobado', '✅ Aprobado'),
        ('en_construccion', '🏗️ En Construcción'),
        ('paralizado', '⚠️ Paralizado'),
        ('completado', '🎉 Completado'),
        ('cancelado', '❌ Cancelado'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('alta', '🔴 Alta'),
        ('media', '🟡 Media'),
        ('baja', '🟢 Baja'),
    ]
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='planificacion',
        verbose_name='Estado del Proyecto'
    )
    
    prioridad = models.CharField(
        max_length=10,
        choices=PRIORIDAD_CHOICES,
        default='media',
        verbose_name='Prioridad'
    )
    
    fecha_inicio = models.DateField(
        null=True, blank=True,
        verbose_name='Fecha de Inicio'
    )
    
    fecha_fin_estimada = models.DateField(
        null=True, blank=True,
        verbose_name='Fecha Estimada de Finalización'
    )
    
    fecha_fin_real = models.DateField(
        null=True, blank=True,
        verbose_name='Fecha Real de Finalización'
    )
    
    responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='proyectos_asignados',
        verbose_name='Responsable del Proyecto'
    )
    
    presupuesto_estimado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True, blank=True,
        verbose_name='Presupuesto Estimado (S/)'
    )
    
    presupuesto_gastado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Presupuesto Gastado (S/)'
    )
    
    progreso_porcentaje = models.PositiveIntegerField(
        default=0,
        verbose_name='Progreso (%)',
        help_text='Porcentaje de avance del proyecto (0-100)'
    )
    
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones Generales'
    )
    
    # Campos automáticos
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )

    class Meta:
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'
        ordering = ['-fecha_actualizacion']

    def __str__(self):
        return f"{self.codigo} – {self.nombre_edificio}"
    
    @property
    def dias_desde_inicio(self):
        """Días transcurridos desde el inicio del proyecto"""
        if self.fecha_inicio:
            return (timezone.now().date() - self.fecha_inicio).days
        return None
    
    @property
    def dias_retraso(self):
        """Días de retraso respecto a la fecha estimada"""
        if self.fecha_fin_estimada and self.estado not in ['completado', 'cancelado']:
            hoy = timezone.now().date()
            if hoy > self.fecha_fin_estimada:
                return (hoy - self.fecha_fin_estimada).days
        return 0
    
    @property
    def esta_retrasado(self):
        """Indica si el proyecto está retrasado"""
        return self.dias_retraso > 0
    
    @property
    def presupuesto_restante(self):
        """Presupuesto restante"""
        if self.presupuesto_estimado:
            return self.presupuesto_estimado - self.presupuesto_gastado
        return None
    
    @property
    def esta_sobre_presupuesto(self):
        """Indica si el proyecto está sobre presupuesto"""
        if self.presupuesto_estimado:
            return self.presupuesto_gastado > self.presupuesto_estimado
        return False


class SeguimientoProyecto(models.Model):
    """Tabla para registrar el historial de cambios y seguimiento"""
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='seguimientos',
        verbose_name='Proyecto'
    )
    
    fecha_registro = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Registro'
    )
    
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Usuario que Registra'
    )
    
    estado_anterior = models.CharField(
        max_length=20,
        choices=Proyecto.ESTADO_CHOICES,
        null=True, blank=True,
        verbose_name='Estado Anterior'
    )
    
    estado_nuevo = models.CharField(
        max_length=20,
        choices=Proyecto.ESTADO_CHOICES,
        verbose_name='Estado Nuevo'
    )
    
    progreso_anterior = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name='Progreso Anterior (%)'
    )
    
    progreso_nuevo = models.PositiveIntegerField(
        verbose_name='Progreso Nuevo (%)'
    )
    
    comentario = models.TextField(
        verbose_name='Comentarios del Cambio'
    )
    
    class Meta:
        verbose_name = 'Seguimiento de Proyecto'
        verbose_name_plural = 'Seguimientos de Proyectos'
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.proyecto.codigo} - {self.fecha_registro.strftime('%d/%m/%Y')}"


class TareaProyecto(models.Model):
    """Tareas específicas dentro de cada proyecto"""
    ESTADO_TAREA_CHOICES = [
        ('pendiente', '⏳ Pendiente'),
        ('en_progreso', '🔄 En Progreso'),
        ('completada', '✅ Completada'),
        ('bloqueada', '🚫 Bloqueada'),
    ]
    
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='tareas',
        verbose_name='Proyecto'
    )
    
    nombre = models.CharField(
        max_length=255,
        verbose_name='Nombre de la Tarea'
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_TAREA_CHOICES,
        default='pendiente',
        verbose_name='Estado de la Tarea'
    )
    
    responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='Responsable'
    )
    
    fecha_inicio = models.DateField(
        null=True, blank=True,
        verbose_name='Fecha de Inicio'
    )
    
    fecha_fin = models.DateField(
        null=True, blank=True,
        verbose_name='Fecha de Finalización'
    )
    
    orden = models.PositiveIntegerField(
        default=1,
        verbose_name='Orden de Ejecución'
    )
    
    class Meta:
        verbose_name = 'Tarea de Proyecto'
        verbose_name_plural = 'Tareas de Proyectos'
        ordering = ['proyecto', 'orden']

    def __str__(self):
        return f"{self.proyecto.codigo} - {self.nombre}"