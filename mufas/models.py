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