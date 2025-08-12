# roles/models.py - Sistema de Roles por Áreas de WinFibra
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class AreaTrabajo(models.Model):
    """Áreas de trabajo de la empresa"""
    AREAS_CHOICES = [
        ('comercial', 'Área Comercial'),
        ('planificacion', 'Área de Planificación'), 
        ('construccion', 'Área de Construcción'),
        ('administracion', 'Administración'),
    ]
    
    codigo = models.CharField(
        max_length=20,
        choices=AREAS_CHOICES,
        unique=True,
        verbose_name='Código del Área'
    )
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre del Área'
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    activa = models.BooleanField(
        default=True,
        verbose_name='Área Activa'
    )
    
    class Meta:
        verbose_name = 'Área de Trabajo'
        verbose_name_plural = 'Áreas de Trabajo'
        ordering = ['codigo']
    
    def __str__(self):
        return f"{self.get_codigo_display()}"


class RolUsuario(models.Model):
    """Roles específicos dentro de cada área"""
    ROLES_CHOICES = [
        # Área Comercial
        ('comercial', 'Comercial'),
        ('supervisor_comercial', 'Supervisor Comercial'),
        
        # Área de Planificación  
        ('planificador', 'Planificador'),
        ('supervisor_planificacion', 'Supervisor de Planificación'),
        
        # Área de Construcción
        ('constructor', 'Constructor'),
        ('supervisor_construccion', 'Supervisor de Construcción'),
        
        # Administración
        ('admin_sistema', 'Administrador del Sistema'),
    ]
    
    codigo = models.CharField(
        max_length=30,
        choices=ROLES_CHOICES,
        unique=True,
        verbose_name='Código del Rol'
    )
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre del Rol'
    )
    area = models.ForeignKey(
        AreaTrabajo,
        on_delete=models.CASCADE,
        related_name='roles',
        verbose_name='Área de Trabajo'
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción del Rol'
    )
    permisos_especiales = models.ManyToManyField(
        Permission,
        blank=True,
        verbose_name='Permisos Especiales'
    )
    
    class Meta:
        verbose_name = 'Rol de Usuario'
        verbose_name_plural = 'Roles de Usuario'
        ordering = ['area', 'codigo']
    
    def __str__(self):
        return f"{self.get_codigo_display()} ({self.area.nombre})"


class PerfilUsuario(models.Model):
    """Perfil extendido del usuario con rol y área"""
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name='Usuario'
    )
    rol = models.ForeignKey(
        RolUsuario,
        on_delete=models.PROTECT,
        related_name='usuarios',
        verbose_name='Rol'
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono'
    )
    dni = models.CharField(
        max_length=8,
        blank=True,
        verbose_name='DNI'
    )
    fecha_ingreso = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Ingreso'
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Usuario Activo'
    )
    
    # Configuraciones de interfaz
    puede_ver_dashboard = models.BooleanField(default=True)
    puede_crear_proyectos = models.BooleanField(default=False)
    puede_editar_proyectos = models.BooleanField(default=False)
    puede_asignar_hilos = models.BooleanField(default=False)
    puede_ver_mapa_mufas = models.BooleanField(default=True)
    puede_ver_analytics = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
        ordering = ['rol__area', 'usuario__username']
    
    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} - {self.rol}"
    
    @property
    def area_trabajo(self):
        """Obtener el área de trabajo del usuario"""
        return self.rol.area
    
    @property
    def es_supervisor(self):
        """Verificar si el usuario es supervisor de su área"""
        return 'supervisor' in self.rol.codigo
    
    @property
    def puede_supervisar_area(self):
        """Verificar si puede supervisar su área"""
        return self.es_supervisor and self.activo


# Signals para crear perfil automáticamente
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Crear perfil automáticamente al crear usuario"""
    if created:
        # Asignar rol por defecto (comercial) si no se especifica
        try:
            rol_default = RolUsuario.objects.get(codigo='comercial')
            PerfilUsuario.objects.create(
                usuario=instance,
                rol=rol_default
            )
        except RolUsuario.DoesNotExist:
            # Si no existe el rol comercial, no crear perfil automático
            pass

@receiver(post_save, sender=User) 
def guardar_perfil_usuario(sender, instance, **kwargs):
    """Guardar perfil al guardar usuario"""
    if hasattr(instance, 'perfil'):
        instance.perfil.save()


class RegistroAcceso(models.Model):
    """Registro de accesos y acciones por área"""
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Usuario'
    )
    accion = models.CharField(
        max_length=100,
        verbose_name='Acción Realizada'
    )
    modulo = models.CharField(
        max_length=50,
        verbose_name='Módulo'
    )
    fecha_hora = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha y Hora'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Dirección IP'
    )
    detalles = models.TextField(
        blank=True,
        verbose_name='Detalles de la Acción'
    )
    
    class Meta:
        verbose_name = 'Registro de Acceso'
        verbose_name_plural = 'Registros de Acceso'
        ordering = ['-fecha_hora']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.accion} ({self.fecha_hora.strftime('%d/%m/%Y %H:%M')})"