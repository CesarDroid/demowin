# planificacion/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
import json

from mufas.models import Mufa, CableTroncal, CableSlot, CableDerivacion, Hilo
from proyectos.models import Proyecto
from .forms import (
    LoginForm, MufaForm, CableTroncalForm, CableDerivacionForm, 
    CableSlotForm
)

# ========== AUTENTICACIÓN ==========

def login_view(request):
    """
    Vista de login personalizada para el área de planificación
    """
    if request.user.is_authenticated:
        return redirect('planificacion:dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenido al área de Planificación, {user.get_full_name() or user.username}')
                return redirect('planificacion:dashboard')
            else:
                messages.error(request, 'Credenciales inválidas. Contacte al administrador del sistema.')
    else:
        form = LoginForm()
    
    return render(request, 'planificacion/login.html', {'form': form})

@login_required
def logout_view(request):
    """
    Cerrar sesión
    """
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente')
    return redirect('planificacion:login')

# ========== DASHBOARD ==========

@login_required
def dashboard(request):
    """
    Dashboard principal del área de planificación
    """
    # Estadísticas generales
    stats = {
        'total_mufas': Mufa.objects.count(),
        'mufas_por_tipo': {
            item['tipo']: item['count'] 
            for item in Mufa.objects.values('tipo').annotate(count=Count('tipo'))
        },
        'total_cables_troncales': CableTroncal.objects.count(),
        'total_derivaciones': CableDerivacion.objects.count(),
        'derivaciones_por_estado': {
            item['estado']: item['count']
            for item in CableDerivacion.objects.values('estado').annotate(count=Count('estado'))
        },
        'slots_disponibles': CableSlot.objects.filter(estado='libre').count(),
        'slots_ocupados': CableSlot.objects.filter(estado='ocupado').count(),
    }
    
    # Proyectos activos
    proyectos_activos = Proyecto.objects.filter(
        estado__in=['planificacion', 'aprobado', 'en_construccion']
    ).count()
    
    # Hilos disponibles
    hilos_stats = {
        'libres': Hilo.objects.filter(estado='libre').count(),
        'ocupados': Hilo.objects.filter(estado='ocupado').count(),
        'reservados': Hilo.objects.filter(estado='reservado').count(),
    }
    
    # Actividad reciente - derivaciones creadas últimos 30 días
    from django.utils import timezone
    from datetime import timedelta
    
    fecha_limite = timezone.now() - timedelta(days=30)
    derivaciones_recientes = CableDerivacion.objects.filter(
        fecha_creacion__gte=fecha_limite
    ).select_related('mufa_origen', 'proyecto')[:10]
    
    context = {
        'stats': stats,
        'proyectos_activos': proyectos_activos,
        'hilos_stats': hilos_stats,
        'derivaciones_recientes': derivaciones_recientes,
    }
    
    return render(request, 'planificacion/dashboard.html', context)

# ========== GESTIÓN DE MUFAS ==========

@login_required
def mufas_list(request):
    """
    Lista de mufas con filtros y búsqueda
    """
    mufas = Mufa.objects.select_related('cable_troncal').prefetch_related('hilos')
    
    # Filtros
    tipo = request.GET.get('tipo')
    distrito = request.GET.get('distrito')
    search = request.GET.get('search')
    
    if tipo and tipo != 'todos':
        mufas = mufas.filter(tipo=tipo)
    
    if distrito and distrito != 'todos':
        mufas = mufas.filter(distrito__icontains=distrito)
    
    if search:
        mufas = mufas.filter(
            Q(codigo__icontains=search) |
            Q(descripcion__icontains=search) |
            Q(ubicacion__icontains=search)
        )
    
    # Paginación
    paginator = Paginator(mufas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Opciones para filtros
    tipos_disponibles = Mufa.TIPO_MUFA
    distritos_disponibles = Mufa.objects.values_list('distrito', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'tipos_disponibles': tipos_disponibles,
        'distritos_disponibles': distritos_disponibles,
        'current_filters': {
            'tipo': tipo,
            'distrito': distrito,
            'search': search,
        }
    }
    
    return render(request, 'planificacion/mufas/list.html', context)

@login_required
def mufa_create(request):
    """
    Crear nueva mufa
    """
    if request.method == 'POST':
        form = MufaForm(request.POST)
        if form.is_valid():
            mufa = form.save()
            messages.success(request, f'Mufa {mufa.codigo} creada exitosamente')
            return redirect('planificacion:mufa_detail', pk=mufa.pk)
    else:
        form = MufaForm()
    
    return render(request, 'planificacion/mufas/create.html', {'form': form})

@login_required
def mufa_detail(request, pk):
    """
    Detalle de mufa con información completa
    """
    mufa = get_object_or_404(Mufa, pk=pk)
    
    # Información relacionada
    hilos = mufa.hilos.all().order_by('numero')
    slots = mufa.cable_slots.all().order_by('numero_slot')
    derivaciones = mufa.cables_derivacion.all().order_by('codigo')
    
    context = {
        'mufa': mufa,
        'hilos': hilos,
        'slots': slots,
        'derivaciones': derivaciones,
        'stats': {
            'hilos_libres': hilos.filter(estado='libre').count(),
            'hilos_ocupados': hilos.filter(estado='ocupado').count(),
            'hilos_reservados': hilos.filter(estado='reservado').count(),
            'slots_libres': slots.filter(estado='libre').count(),
            'slots_ocupados': slots.filter(estado='ocupado').count(),
        }
    }
    
    return render(request, 'planificacion/mufas/detail.html', context)

@login_required
def mufa_edit(request, pk):
    """
    Editar mufa existente
    """
    mufa = get_object_or_404(Mufa, pk=pk)
    
    if request.method == 'POST':
        form = MufaForm(request.POST, instance=mufa)
        if form.is_valid():
            form.save()
            messages.success(request, f'Mufa {mufa.codigo} actualizada exitosamente')
            return redirect('planificacion:mufa_detail', pk=mufa.pk)
    else:
        form = MufaForm(instance=mufa)
    
    return render(request, 'planificacion/mufas/edit.html', {
        'form': form, 
        'mufa': mufa
    })

@login_required
@require_http_methods(["POST"])
def mufa_delete(request, pk):
    """
    Eliminar mufa (con confirmación)
    """
    mufa = get_object_or_404(Mufa, pk=pk)
    codigo = mufa.codigo
    
    try:
        mufa.delete()
        messages.success(request, f'Mufa {codigo} eliminada exitosamente')
    except Exception as e:
        messages.error(request, f'Error al eliminar mufa: {str(e)}')
    
    return redirect('planificacion:mufas_list')

# ========== GESTIÓN DE CABLES TRONCALES ==========

@login_required
def cables_troncales_list(request):
    """
    Lista de cables troncales
    """
    cables = CableTroncal.objects.prefetch_related('mufas').all()
    
    # Agregar estadísticas
    for cable in cables:
        cable.mufas_conectadas = cable.mufas.count()
        cable.slots_utilizados = CableSlot.objects.filter(
            cable_troncal=cable, 
            estado='ocupado'
        ).count()
    
    return render(request, 'planificacion/cables_troncales/list.html', {
        'cables': cables
    })

@login_required
def cable_troncal_create(request):
    """
    Crear nuevo cable troncal
    """
    if request.method == 'POST':
        form = CableTroncalForm(request.POST)
        if form.is_valid():
            cable = form.save()
            messages.success(request, f'Cable troncal {cable.codigo} creado exitosamente')
            return redirect('planificacion:cable_troncal_detail', pk=cable.pk)
    else:
        form = CableTroncalForm()
    
    return render(request, 'planificacion/cables_troncales/create.html', {'form': form})

@login_required
def cable_troncal_detail(request, pk):
    """
    Detalle de cable troncal
    """
    cable = get_object_or_404(CableTroncal, pk=pk)
    mufas_conectadas = cable.mufas.all()
    slots_utilizados = CableSlot.objects.filter(cable_troncal=cable)
    
    context = {
        'cable': cable,
        'mufas_conectadas': mufas_conectadas,
        'slots_utilizados': slots_utilizados,
        'stats': {
            'mufas_count': mufas_conectadas.count(),
            'slots_libres': slots_utilizados.filter(estado='libre').count(),
            'slots_ocupados': slots_utilizados.filter(estado='ocupado').count(),
        }
    }
    
    return render(request, 'planificacion/cables_troncales/detail.html', context)

@login_required
def cable_troncal_edit(request, pk):
    """
    Editar cable troncal
    """
    cable = get_object_or_404(CableTroncal, pk=pk)
    
    if request.method == 'POST':
        form = CableTroncalForm(request.POST, instance=cable)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cable troncal {cable.codigo} actualizado exitosamente')
            return redirect('planificacion:cable_troncal_detail', pk=cable.pk)
    else:
        form = CableTroncalForm(instance=cable)
    
    return render(request, 'planificacion/cables_troncales/edit.html', {
        'form': form, 
        'cable': cable
    })

# ========== GESTIÓN DE DERIVACIONES ==========

@login_required
def derivaciones_list(request):
    """
    Lista de cables de derivación
    """
    derivaciones = CableDerivacion.objects.select_related(
        'mufa_origen', 'slot_origen', 'proyecto'
    ).all()
    
    # Filtros
    estado = request.GET.get('estado')
    tipo_destino = request.GET.get('tipo_destino')
    mufa = request.GET.get('mufa')
    
    if estado and estado != 'todos':
        derivaciones = derivaciones.filter(estado=estado)
    
    if tipo_destino and tipo_destino != 'todos':
        derivaciones = derivaciones.filter(tipo_destino=tipo_destino)
    
    if mufa and mufa != 'todos':
        derivaciones = derivaciones.filter(mufa_origen__codigo=mufa)
    
    # Paginación
    paginator = Paginator(derivaciones, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Opciones para filtros
    estados_disponibles = CableDerivacion.ESTADO_CABLE_CHOICES
    tipos_destino_disponibles = CableDerivacion.TIPO_DESTINO_CHOICES
    mufas_disponibles = Mufa.objects.values_list('codigo', flat=True)
    
    context = {
        'page_obj': page_obj,
        'estados_disponibles': estados_disponibles,
        'tipos_destino_disponibles': tipos_destino_disponibles,
        'mufas_disponibles': mufas_disponibles,
        'current_filters': {
            'estado': estado,
            'tipo_destino': tipo_destino,
            'mufa': mufa,
        }
    }
    
    return render(request, 'planificacion/derivaciones/list.html', context)

@login_required
def derivacion_create(request):
    """
    Crear nueva derivación
    """
    if request.method == 'POST':
        form = CableDerivacionForm(request.POST)
        if form.is_valid():
            derivacion = form.save()
            messages.success(request, f'Cable de derivación {derivacion.codigo} creado exitosamente')
            return redirect('planificacion:derivacion_detail', pk=derivacion.pk)
    else:
        form = CableDerivacionForm()
    
    return render(request, 'planificacion/derivaciones/create.html', {'form': form})

@login_required
def derivacion_detail(request, pk):
    """
    Detalle de derivación
    """
    derivacion = get_object_or_404(
        CableDerivacion.objects.select_related(
            'mufa_origen', 'slot_origen', 'proyecto'
        ), 
        pk=pk
    )
    
    return render(request, 'planificacion/derivaciones/detail.html', {
        'derivacion': derivacion
    })

@login_required
def derivacion_edit(request, pk):
    """
    Editar derivación
    """
    derivacion = get_object_or_404(CableDerivacion, pk=pk)
    
    if request.method == 'POST':
        form = CableDerivacionForm(request.POST, instance=derivacion)
        if form.is_valid():
            form.save()
            messages.success(request, f'Derivación {derivacion.codigo} actualizada exitosamente')
            return redirect('planificacion:derivacion_detail', pk=derivacion.pk)
    else:
        form = CableDerivacionForm(instance=derivacion)
    
    return render(request, 'planificacion/derivaciones/edit.html', {
        'form': form, 
        'derivacion': derivacion
    })

@login_required
@require_http_methods(["POST"])
def derivacion_delete(request, pk):
    """
    Eliminar derivación
    """
    derivacion = get_object_or_404(CableDerivacion, pk=pk)
    codigo = derivacion.codigo
    
    try:
        derivacion.delete()
        messages.success(request, f'Derivación {codigo} eliminada exitosamente')
    except Exception as e:
        messages.error(request, f'Error al eliminar derivación: {str(e)}')
    
    return redirect('planificacion:derivaciones_list')

# ========== GESTIÓN DE SLOTS ==========

@login_required
def slots_list(request):
    """
    Lista de slots de cables
    """
    slots = CableSlot.objects.select_related(
        'mufa', 'cable_troncal'
    ).all().order_by('mufa__codigo', 'numero_slot')
    
    return render(request, 'planificacion/slots/list.html', {'slots': slots})

@login_required
def slot_create(request):
    """
    Crear nuevo slot
    """
    if request.method == 'POST':
        form = CableSlotForm(request.POST)
        if form.is_valid():
            slot = form.save()
            messages.success(request, f'Slot {slot.numero_slot} creado exitosamente')
            return redirect('planificacion:mufa_detail', pk=slot.mufa.pk)
    else:
        form = CableSlotForm()
    
    return render(request, 'planificacion/slots/create.html', {'form': form})

@login_required
def slot_edit(request, pk):
    """
    Editar slot
    """
    slot = get_object_or_404(CableSlot, pk=pk)
    
    if request.method == 'POST':
        form = CableSlotForm(request.POST, instance=slot)
        if form.is_valid():
            form.save()
            messages.success(request, f'Slot {slot.numero_slot} actualizado exitosamente')
            return redirect('planificacion:mufa_detail', pk=slot.mufa.pk)
    else:
        form = CableSlotForm(instance=slot)
    
    return render(request, 'planificacion/slots/edit.html', {
        'form': form, 
        'slot': slot
    })

# ========== APIs ==========

@login_required
def api_mufas(request):
    """
    API para datatables de mufas
    """
    mufas = Mufa.objects.select_related('cable_troncal').prefetch_related('hilos')
    
    data = []
    for mufa in mufas:
        hilos = mufa.hilos.all()
        data.append({
            'id': mufa.id,
            'codigo': mufa.codigo,
            'tipo': mufa.get_tipo_display(),
            'ubicacion': mufa.ubicacion or 'Sin especificar',
            'distrito': mufa.distrito or 'Sin especificar',
            'capacidad': mufa.capacidad_hilos,
            'hilos_libres': hilos.filter(estado='libre').count(),
            'hilos_ocupados': hilos.filter(estado='ocupado').count(),
            'cable_troncal': mufa.cable_troncal.codigo if mufa.cable_troncal else 'Sin asignar',
            'acciones': mufa.pk,
        })
    
    return JsonResponse({'data': data})

@login_required
def api_derivaciones(request):
    """
    API para datatables de derivaciones
    """
    derivaciones = CableDerivacion.objects.select_related(
        'mufa_origen', 'proyecto'
    ).all()
    
    data = []
    for der in derivaciones:
        data.append({
            'id': der.id,
            'codigo': der.codigo,
            'mufa_origen': der.mufa_origen.codigo,
            'destino': der.nombre_destino,
            'tipo_destino': der.get_tipo_destino_display(),
            'estado': der.get_estado_display(),
            'cliente': der.cliente or 'Sin cliente',
            'proyecto': der.proyecto.codigo if der.proyecto else 'Sin proyecto',
            'fecha_creacion': der.fecha_creacion.strftime('%d/%m/%Y'),
            'acciones': der.pk,
        })
    
    return JsonResponse({'data': data})

@login_required
def api_estadisticas(request):
    """
    API para widgets del dashboard
    """
    stats = {
        'mufas': {
            'total': Mufa.objects.count(),
            'por_tipo': list(Mufa.objects.values('tipo').annotate(count=Count('tipo')))
        },
        'derivaciones': {
            'total': CableDerivacion.objects.count(),
            'por_estado': list(CableDerivacion.objects.values('estado').annotate(count=Count('estado')))
        },
        'hilos': {
            'libres': Hilo.objects.filter(estado='libre').count(),
            'ocupados': Hilo.objects.filter(estado='ocupado').count(),
            'reservados': Hilo.objects.filter(estado='reservado').count(),
        }
    }
    
    return JsonResponse(stats)