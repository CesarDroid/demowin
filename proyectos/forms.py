# proyectos/forms.py - VERSIÓN EXTENDIDA
from django import forms
from django.contrib.auth.models import User
from .models import Proyecto, SeguimientoProyecto, TareaProyecto

class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = [
            'codigo',
            'nombre_edificio',
            'direccion',
            'departamento',
            'distrito',
            'latitud',
            'longitud',
            'cantidad_pisos',
            'cantidad_departamentos',
            'estado',
            'prioridad',
            'fecha_inicio',
            'fecha_fin_estimada',
            'responsable',
            'presupuesto_estimado',
            'progreso_porcentaje',
            'observaciones',
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: PRY001'
            }),
            'nombre_edificio': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del edificio'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección completa'
            }),
            'departamento': forms.TextInput(attrs={
                'class': 'form-control',
                'value': 'Lima',
            }),
            'distrito': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Distrito'
            }),
            'latitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': '-12.0464'
            }),
            'longitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': '-77.0428'
            }),
            'cantidad_pisos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'cantidad_departamentos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'prioridad': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_fin_estimada': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'responsable': forms.Select(attrs={
                'class': 'form-select'
            }),
            'presupuesto_estimado': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '50000.00'
            }),
            'progreso_porcentaje': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'placeholder': '0'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones generales del proyecto...'
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar usuarios activos para el campo responsable
        self.fields['responsable'].queryset = User.objects.filter(
            is_active=True
        ).order_by('first_name', 'last_name', 'username')
        # Campo opcional
        self.fields['responsable'].empty_label = "Seleccionar responsable..."
        
    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        if codigo:
            codigo = codigo.upper().strip()
        return codigo
    
    def clean_progreso_porcentaje(self):
        progreso = self.cleaned_data.get('progreso_porcentaje')
        if progreso is not None and (progreso < 0 or progreso > 100):
            raise forms.ValidationError('El progreso debe estar entre 0 y 100%')
        return progreso


class SeguimientoProyectoForm(forms.ModelForm):
    class Meta:
        model = SeguimientoProyecto
        fields = [
            'estado_nuevo',
            'progreso_nuevo',
            'comentario'
        ]
        widgets = {
            'estado_nuevo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'progreso_nuevo': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100'
            }),
            'comentario': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe los cambios realizados...',
                'required': True
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.proyecto = kwargs.pop('proyecto', None)
        super().__init__(*args, **kwargs)
        
        if self.proyecto:
            # Pre-llenar con valores actuales del proyecto
            self.fields['estado_nuevo'].initial = self.proyecto.estado
            self.fields['progreso_nuevo'].initial = self.proyecto.progreso_porcentaje


class TareaProyectoForm(forms.ModelForm):
    class Meta:
        model = TareaProyecto
        fields = [
            'nombre',
            'descripcion',
            'estado',
            'responsable',
            'fecha_inicio',
            'fecha_fin',
            'orden'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la tarea'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Descripción detallada...'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'responsable': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_fin': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'orden': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['responsable'].queryset = User.objects.filter(
            is_active=True
        ).order_by('first_name', 'last_name', 'username')
        self.fields['responsable'].empty_label = "Sin asignar"


class ProyectoFiltroForm(forms.Form):
    """Formulario para filtrar proyectos en el dashboard"""
    ESTADO_CHOICES = [('', 'Todos los estados')] + Proyecto.ESTADO_CHOICES
    PRIORIDAD_CHOICES = [('', 'Todas las prioridades')] + Proyecto.PRIORIDAD_CHOICES
    
    estado = forms.ChoiceField(
        choices=ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    prioridad = forms.ChoiceField(
        choices=PRIORIDAD_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    responsable = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        empty_label="Todos los responsables",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    distrito = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filtrar por distrito...'
        })
    )
    
    solo_retrasados = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    solo_sobre_presupuesto = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )