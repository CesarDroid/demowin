# planificacion/forms.py
from django import forms
from django.contrib.auth import authenticate
from mufas.models import Mufa, CableTroncal, CableSlot, CableDerivacion
from proyectos.models import Proyecto

class LoginForm(forms.Form):
    """
    Formulario de login personalizado para planificación
    """
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Usuario',
            'autofocus': True,
        }),
        label='Usuario'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Contraseña',
        }),
        label='Contraseña'
    )

class MufaForm(forms.ModelForm):
    """
    Formulario para crear/editar mufas
    """
    class Meta:
        model = Mufa
        fields = [
            'codigo', 'tipo', 'cable_troncal', 'descripcion', 
            'ubicacion', 'latitud', 'longitud', 'capacidad_hilos', 'distrito'
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: MF001'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cable_troncal': forms.Select(attrs={
                'class': 'form-select'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la mufa'
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección o referencia de ubicación'
            }),
            'latitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': 'Ej: -12.0464'
            }),
            'longitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': 'Ej: -77.0428'
            }),
            'capacidad_hilos': forms.Select(attrs={
                'class': 'form-select'
            }),
            'distrito': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Distrito'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar cables troncales activos
        self.fields['cable_troncal'].queryset = CableTroncal.objects.all()
        self.fields['cable_troncal'].empty_label = "Seleccionar cable troncal (opcional)"

class CableTroncalForm(forms.ModelForm):
    """
    Formulario para crear/editar cables troncales
    """
    class Meta:
        model = CableTroncal
        fields = ['codigo', 'descripcion', 'capacidad']
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: CT-MAIN-001'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del cable troncal'
            }),
            'capacidad': forms.Select(attrs={
                'class': 'form-select'
            })
        }

class CableSlotForm(forms.ModelForm):
    """
    Formulario para crear/editar slots de cables
    """
    class Meta:
        model = CableSlot
        fields = [
            'mufa', 'numero_slot', 'tipo_cable', 'cable_troncal', 
            'estado', 'hilos_utilizados', 'descripcion', 'fecha_instalacion'
        ]
        widgets = {
            'mufa': forms.Select(attrs={
                'class': 'form-select'
            }),
            'numero_slot': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'tipo_cable': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cable_troncal': forms.Select(attrs={
                'class': 'form-select'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'hilos_utilizados': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'descripcion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción del slot'
            }),
            'fecha_instalacion': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cable_troncal'].empty_label = "Sin cable asignado"
        self.fields['fecha_instalacion'].required = False

class CableDerivacionForm(forms.ModelForm):
    """
    Formulario para crear/editar cables de derivación
    """
    class Meta:
        model = CableDerivacion
        fields = [
            'codigo', 'mufa_origen', 'slot_origen', 'nombre_destino',
            'tipo_destino', 'direccion_destino', 'latitud_destino',
            'longitud_destino', 'capacidad', 'longitud_metros', 'estado',
            'cliente', 'numero_contrato', 'proyecto', 'tecnico_instalador',
            'observaciones'
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: CD-MF001-001'
            }),
            'mufa_origen': forms.Select(attrs={
                'class': 'form-select',
                'onchange': 'updateSlotsDisponibles()'
            }),
            'slot_origen': forms.Select(attrs={
                'class': 'form-select'
            }),
            'nombre_destino': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del edificio, local, etc.'
            }),
            'tipo_destino': forms.Select(attrs={
                'class': 'form-select'
            }),
            'direccion_destino': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Dirección completa del destino'
            }),
            'latitud_destino': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': 'Ej: -12.0464'
            }),
            'longitud_destino': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': 'Ej: -77.0428'
            }),
            'capacidad': forms.Select(attrs={
                'class': 'form-select'
            }),
            'longitud_metros': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Longitud en metros'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del cliente'
            }),
            'numero_contrato': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de contrato'
            }),
            'proyecto': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tecnico_instalador': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del técnico instalador'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones técnicas'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar querysets
        self.fields['proyecto'].queryset = Proyecto.objects.filter(
            estado__in=['planificacion', 'aprobado', 'en_construccion']
        )
        self.fields['proyecto'].empty_label = "Sin proyecto asignado"
        
        # Si estamos editando, filtrar slots por mufa origen
        if self.instance.pk and self.instance.mufa_origen:
            self.fields['slot_origen'].queryset = CableSlot.objects.filter(
                mufa=self.instance.mufa_origen,
                tipo_cable='derivacion'
            )
        else:
            self.fields['slot_origen'].queryset = CableSlot.objects.filter(
                tipo_cable='derivacion'
            )
        
        self.fields['slot_origen'].empty_label = "Seleccionar slot de derivación"
    
    def clean(self):
        cleaned_data = super().clean()
        mufa_origen = cleaned_data.get('mufa_origen')
        slot_origen = cleaned_data.get('slot_origen')
        
        # Validar que el slot pertenezca a la mufa origen
        if mufa_origen and slot_origen:
            if slot_origen.mufa != mufa_origen:
                raise forms.ValidationError({
                    'slot_origen': 'El slot seleccionado no pertenece a la mufa origen.'
                })
            
            if slot_origen.tipo_cable != 'derivacion':
                raise forms.ValidationError({
                    'slot_origen': 'El slot debe ser de tipo derivación.'
                })
        
        return cleaned_data

# Formulario de búsqueda avanzada
class BusquedaAvanzadaForm(forms.Form):
    """
    Formulario para búsquedas avanzadas en el sistema
    """
    TIPO_BUSQUEDA = [
        ('mufas', 'Mufas'),
        ('derivaciones', 'Cables de Derivación'),
        ('slots', 'Slots de Cables'),
    ]
    
    tipo_busqueda = forms.ChoiceField(
        choices=TIPO_BUSQUEDA,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tipo de búsqueda'
    )
    
    termino = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese términos de búsqueda...'
        }),
        label='Término de búsqueda'
    )
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Fecha desde'
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Fecha hasta'
    )