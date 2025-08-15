# mufas/models.py - VERSIÓN CORREGIDA Y COMPATIBLE
from django.db import models

class CableTroncal(models.Model):
    CAPACIDAD_CHOICES = [
        (12,  '12 hilos'),
        (24,  '24 hilos'),
        (48,  '48 hilos'),
        (64,  '64 hilos'),
        (96,  '96 hilos'),
        (128, '128 hilos'),
    ]

    codigo      = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Código'
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    capacidad   = models.IntegerField(
        choices=CAPACIDAD_CHOICES,
        verbose_name='Capacidad (hilos)'
    )

    class Meta:
        verbose_name        = 'Cable Troncal'
        verbose_name_plural = 'Cables Troncales'
        ordering            = ['codigo']

    def __str__(self):
        return f"{self.codigo} ({self.get_capacidad_display()})"


class Mufa(models.Model):
    TIPO_MUFA = [
        ('troncal',    'Mufa Troncal'),
        ('derivacion', 'Mufa de Derivación'),
        ('final',      'Mufa Final User'),
    ]

    OPCIONES_CAPACIDAD = [
        (12,  '12 hilos'),
        (24,  '24 hilos'),
        (48,  '48 hilos'),
        (64,  '64 hilos'),
        (96,  '96 hilos'),
        (128, '128 hilos'),
    ]

    cable_troncal   = models.ForeignKey(
        CableTroncal,
        on_delete=models.PROTECT,
        related_name='mufas',
        verbose_name='Cable Troncal',
        null=True,
        blank=True,
    )
    codigo          = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Código'
    )
    tipo            = models.CharField(
        max_length=20,
        choices=TIPO_MUFA,
        default='troncal',
        verbose_name='Tipo de Mufa'
    )
    descripcion     = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    ubicacion       = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Ubicación'
    )
    latitud         = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Latitud'
    )
    longitud        = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Longitud'
    )
    capacidad_hilos = models.IntegerField(
        choices=OPCIONES_CAPACIDAD,
        default=12,
        verbose_name='Capacidad de hilos'
    )
    distrito        = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Distrito'
    )

    class Meta:
        verbose_name        = 'Mufa'
        verbose_name_plural = 'Mufas'
        ordering            = ['codigo']

    def __str__(self):
        return f"Mufa [{self.codigo}]"

    @property
    def hilos_libres(self):
        return self.hilos.filter(estado='libre').count()

    @property
    def hilos_ocupados(self):
        return self.hilos.filter(estado='ocupado').count()

    @property
    def hilos_reservados(self):
        return self.hilos.filter(estado='reservado').count()

    @property
    def porcentaje_ocupacion(self):
        total = self.hilos.count()
        if total > 0:
            return round((self.hilos_ocupados / total) * 100, 1)
        return 0


class Hilo(models.Model):
    mufa     = models.ForeignKey(
        Mufa,
        related_name='hilos',
        on_delete=models.CASCADE,
        verbose_name='Mufa'
    )
    numero   = models.IntegerField(verbose_name='Nº de hilo')
    estado   = models.CharField(
        max_length=50,
        choices=[
            ('libre',    'Libre'),
            ('ocupado',  'Ocupado'),
            ('reservado','Reservado'),
        ],
        default='libre',
        verbose_name='Estado'
    )
    uso       = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Uso/Proyecto'
    )
    splitter  = models.CharField(
        max_length=10,
        choices=[
            ('1:1', '1:1'),
            ('1:4', '1:4'),
            ('1:8', '1:8'),
            ('-',   'Sin splitter'),
        ],
        default='-',
        verbose_name='Splitter'
    )
    destino   = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Destino'
    )

    class Meta:
        verbose_name        = 'Hilo'
        verbose_name_plural = 'Hilos'
        ordering            = ['mufa', 'numero']
        unique_together     = [['mufa', 'numero']]

    def __str__(self):
        return f"Hilo {self.numero} – {self.mufa.codigo}"


class CableSlot(models.Model):
    TIPO_CABLE_CHOICES = [
        ('ingreso', 'Cable de Ingreso'),
        ('salida', 'Cable de Salida'),
        ('derivacion', 'Cable de Derivación'),
    ]
    
    ESTADO_SLOT_CHOICES = [
        ('libre', 'Libre'),
        ('ocupado', 'Ocupado'),
        ('reservado', 'Reservado'),
        ('fuera_servicio', 'Fuera de Servicio'),
    ]

    mufa = models.ForeignKey(
        Mufa,
        related_name='cable_slots',
        on_delete=models.CASCADE,
        verbose_name='Mufa'
    )
    cable_troncal = models.ForeignKey(
        CableTroncal,
        on_delete=models.PROTECT,
        related_name='slots',
        verbose_name='Cable Troncal',
        null=True,
        blank=True,
    )
    tipo_cable = models.CharField(
        max_length=20,
        choices=TIPO_CABLE_CHOICES,
        verbose_name='Tipo de Cable'
    )
    numero_slot = models.IntegerField(
        verbose_name='Número de Slot',
        help_text='Posición física en la mufa'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_SLOT_CHOICES,
        default='libre',
        verbose_name='Estado del Slot'
    )
    descripcion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Descripción',
        help_text='Describe el uso específico o destino del cable'
    )
    hilos_utilizados = models.IntegerField(
        default=0,
        verbose_name='Hilos Utilizados',
        help_text='Número de hilos en uso en este slot'
    )
    fecha_instalacion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Instalación'
    )

    class Meta:
        verbose_name = 'Slot de Cable'
        verbose_name_plural = 'Slots de Cables'
        ordering = ['mufa__codigo', 'numero_slot']
        unique_together = [['mufa', 'numero_slot']]

    def __str__(self):
        return f"Slot {self.numero_slot} - {self.mufa.codigo} ({self.get_tipo_cable_display()})"

    @property
    def porcentaje_utilizacion(self):
        if self.cable_troncal and self.cable_troncal.capacidad > 0:
            return round((self.hilos_utilizados / self.cable_troncal.capacidad) * 100, 1)
        return 0

    @property
    def hilos_libres(self):
        if self.cable_troncal:
            return self.cable_troncal.capacidad - self.hilos_utilizados
        return 0


class Conexion(models.Model):
    origen        = models.ForeignKey(
        Hilo,
        related_name='conexiones_origen',
        on_delete=models.CASCADE,
        verbose_name='Hilo Origen'
    )
    destino       = models.ForeignKey(
        Hilo,
        related_name='conexiones_destino',
        on_delete=models.CASCADE,
        verbose_name='Hilo Destino'
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones'
    )

    class Meta:
        verbose_name        = 'Conexión'
        verbose_name_plural = 'Conexiones'
        ordering            = ['origen__mufa__codigo', 'origen__numero']
        unique_together     = [['origen', 'destino']]

    def __str__(self):
        return f"{self.origen} → {self.destino}"


class CableDerivacion(models.Model):
    """
    Modelo para cables de derivación que conectan mufas con edificios/usuarios finales.
    Estos cables salen desde un slot de derivación de una mufa hacia un destino específico.
    """
    
    TIPO_DESTINO_CHOICES = [
        ('edificio_residencial', 'Edificio Residencial'),
        ('edificio_comercial', 'Edificio Comercial'),
        ('edificio_industrial', 'Edificio Industrial'),
        ('casa_individual', 'Casa Individual'),
        ('local_comercial', 'Local Comercial'),
        ('oficina', 'Oficina'),
        ('otro', 'Otro'),
    ]
    
    ESTADO_CABLE_CHOICES = [
        ('instalado', 'Instalado'),
        ('planificado', 'Planificado'),
        ('en_construccion', 'En Construcción'),
        ('mantenimiento', 'En Mantenimiento'),
        ('fuera_servicio', 'Fuera de Servicio'),
    ]
    
    CAPACIDAD_CHOICES = [
        (2, '2 hilos'),
        (4, '4 hilos'),
        (6, '6 hilos'),
        (8, '8 hilos'),
        (12, '12 hilos'),
        (24, '24 hilos'),
    ]

    # Información básica del cable
    codigo = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Código del Cable',
        help_text='Código único identificador del cable de derivación'
    )
    
    # Conexión con mufa origen
    mufa_origen = models.ForeignKey(
        Mufa,
        on_delete=models.PROTECT,
        related_name='cables_derivacion',
        verbose_name='Mufa de Origen',
        help_text='Mufa desde donde sale este cable de derivación'
    )
    
    slot_origen = models.ForeignKey(
        CableSlot,
        on_delete=models.PROTECT,
        related_name='cables_derivacion',
        verbose_name='Slot de Origen',
        help_text='Slot específico de la mufa donde se conecta este cable',
        null=True,
        blank=True,
    )
    
    # Información del destino
    nombre_destino = models.CharField(
        max_length=255,
        verbose_name='Nombre del Destino',
        help_text='Nombre del edificio, local o dirección de destino'
    )
    
    tipo_destino = models.CharField(
        max_length=30,
        choices=TIPO_DESTINO_CHOICES,
        default='edificio_residencial',
        verbose_name='Tipo de Destino'
    )
    
    direccion_destino = models.TextField(
        verbose_name='Dirección del Destino',
        help_text='Dirección completa del punto de llegada del cable'
    )
    
    # Coordenadas del destino
    latitud_destino = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Latitud del Destino',
        help_text='Coordenada geográfica del destino'
    )
    
    longitud_destino = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Longitud del Destino',
        help_text='Coordenada geográfica del destino'
    )
    
    # Características técnicas
    capacidad = models.IntegerField(
        choices=CAPACIDAD_CHOICES,
        default=4,
        verbose_name='Capacidad (hilos)',
        help_text='Número total de hilos del cable de derivación'
    )
    
    longitud_metros = models.FloatField(
        verbose_name='Longitud (metros)',
        help_text='Longitud física del cable en metros',
        null=True,
        blank=True,
    )
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CABLE_CHOICES,
        default='planificado',
        verbose_name='Estado del Cable'
    )
    
    # Información de instalación
    fecha_instalacion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Instalación'
    )
    
    tecnico_instalador = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Técnico Instalador',
        help_text='Nombre del técnico que realizó la instalación'
    )
    
    # Información comercial
    cliente = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Cliente',
        help_text='Nombre del cliente o empresa destinataria'
    )
    
    numero_contrato = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Número de Contrato',
        help_text='Número de contrato comercial asociado'
    )
    
    # Observaciones técnicas
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones',
        help_text='Notas técnicas, problemas, o información adicional'
    )
    
    # Información de proyecto
    proyecto = models.ForeignKey(
        'proyectos.Proyecto',
        on_delete=models.SET_NULL,
        related_name='cables_derivacion',
        verbose_name='Proyecto Asociado',
        null=True,
        blank=True,
        help_text='Proyecto al que pertenece esta derivación'
    )
    
    # Timestamps
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Modificación'
    )

    class Meta:
        verbose_name = 'Cable de Derivación'
        verbose_name_plural = 'Cables de Derivación'
        ordering = ['codigo']
        indexes = [
            models.Index(fields=['mufa_origen', 'estado']),
            models.Index(fields=['tipo_destino', 'estado']),
            models.Index(fields=['fecha_instalacion']),
        ]

    def __str__(self):
        return f"{self.codigo} → {self.nombre_destino}"
    
    @property
    def distancia_calculada(self):
        """
        Calcula la distancia en línea recta entre la mufa origen y el destino.
        Útil para estimaciones cuando no se tiene la longitud real del cable.
        """
        if (self.mufa_origen.latitud and self.mufa_origen.longitud and 
            self.latitud_destino and self.longitud_destino):
            
            from geopy.distance import geodesic
            origen = (self.mufa_origen.latitud, self.mufa_origen.longitud)
            destino = (self.latitud_destino, self.longitud_destino)
            return round(geodesic(origen, destino).meters, 2)
        return None
    
    @property
    def hilos_libres(self):
        """
        Calcula la cantidad de hilos libres en este cable de derivación.
        """
        # Por ahora retornamos la capacidad total, después se puede implementar
        # el seguimiento específico de hilos ocupados en derivaciones
        return self.capacidad
    
    @property
    def info_slot_origen(self):
        """
        Información del slot de origen en la mufa.
        """
        if self.slot_origen:
            return f"Slot {self.slot_origen.numero_slot} ({self.slot_origen.get_tipo_cable_display()})"
        return "Sin slot asignado"
    
    @property
    def direccion_completa(self):
        """
        Dirección completa formateada para mostrar.
        """
        partes = [self.nombre_destino, self.direccion_destino]
        return " - ".join(filter(None, partes))
    
    def clean(self):
        """
        Validaciones personalizadas del modelo.
        """
        from django.core.exceptions import ValidationError
        
        # Validar que si se especifica slot, sea de tipo derivación
        if self.slot_origen and self.slot_origen.tipo_cable != 'derivacion':
            raise ValidationError({
                'slot_origen': 'El slot debe ser de tipo derivación para cables de derivación'
            })
        
        # Validar que el slot pertenezca a la mufa origen
        if self.slot_origen and self.slot_origen.mufa != self.mufa_origen:
            raise ValidationError({
                'slot_origen': 'El slot debe pertenecer a la mufa de origen seleccionada'
            })
        
        # Validar coordenadas si se proporcionan
        if self.latitud_destino is not None:
            if not (-90 <= self.latitud_destino <= 90):
                raise ValidationError({
                    'latitud_destino': 'La latitud debe estar entre -90 y 90 grados'
                })
        
        if self.longitud_destino is not None:
            if not (-180 <= self.longitud_destino <= 180):
                raise ValidationError({
                    'longitud_destino': 'La longitud debe estar entre -180 y 180 grados'
                })
    
    def save(self, *args, **kwargs):
        """
        Sobrescribir save para ejecutar validaciones.
        """
        self.clean()
        super().save(*args, **kwargs)
        
        # Actualizar el slot origen como ocupado si no lo está
        if self.slot_origen and self.slot_origen.estado == 'libre':
            self.slot_origen.estado = 'ocupado'
            self.slot_origen.descripcion = f'Cable derivación: {self.codigo}'
            self.slot_origen.save()