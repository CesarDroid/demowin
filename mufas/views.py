# mufas/views.py - VERSIÓN ACTUALIZADA CON CONTROLES

import json
from django.shortcuts              import render, get_object_or_404
from django.http                   import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http  import require_POST
from django.contrib.auth.decorators import login_required, permission_required
from .models                       import Mufa, CableTroncal, Conexion, Hilo
from proyectos.models              import Proyecto

def mapa_mufas(request):
    """
    Renderiza la plantilla HTML con el mapa de Leaflet y controles avanzados.
    """
    return render(request, 'mufas/mapa_mufas_control.html')


def obtener_mufas(request):
    """
    Devuelve un array JSON con todas las mufas que tengan coordenadas,
    su estado (libres/ocupados) y la lista de hilos.
    Incluye información adicional para los filtros del panel de control.
    También incluye la lista de proyectos disponibles para asignación.
    Soporta filtros por cable troncal.
    """
    # Obtener proyectos activos para el dropdown
    proyectos_activos = Proyecto.objects.filter(
        estado__in=['planificacion', 'aprobado', 'en_construccion']
    ).order_by('codigo').values('id', 'codigo', 'nombre_edificio', 'estado')
    
    # Obtener cables troncales para el filtro
    cables_troncales = CableTroncal.objects.all().order_by('codigo').values('id', 'codigo', 'capacidad')
    
    # Aplicar filtros si se especifican
    qs = Mufa.objects.prefetch_related('hilos').select_related('cable_troncal')
    
    # Filtro por cable troncal
    cable_troncal_id = request.GET.get('cable_troncal')
    if cable_troncal_id and cable_troncal_id != 'todos':
        try:
            qs = qs.filter(cable_troncal_id=int(cable_troncal_id))
        except (ValueError, TypeError):
            pass
    
    # Filtro por distrito
    distrito = request.GET.get('distrito')
    if distrito and distrito != 'todos':
        qs = qs.filter(distrito__icontains=distrito)
    
    # Filtro por tipo
    tipo = request.GET.get('tipo')
    if tipo and tipo != 'todos':
        qs = qs.filter(tipo=tipo)
    
    data = []
    
    for m in qs:
        if m.latitud and m.longitud:
            hilos = m.hilos.all()
            libres = sum(1 for h in hilos if h.estado == 'libre')
            ocupados = sum(1 for h in hilos if h.estado == 'ocupado')
            reservados = sum(1 for h in hilos if h.estado == 'reservado')

            hilos_data = [
                {
                    'id'      : h.id,
                    'numero'  : h.numero,
                    'estado'  : h.estado,
                    'uso'     : h.uso or '',
                    'splitter': h.splitter,
                    'destino' : h.destino or '',
                }
                for h in hilos
            ]

            data.append({
                'codigo'     : m.codigo,
                'tipo'       : m.tipo,  # ← Agregado para filtros
                'descripcion': m.descripcion or '',
                'ubicacion'  : m.ubicacion or '',  # ← Agregado
                'distrito'   : m.distrito or '',   # ← Agregado para filtros
                'latitud'    : m.latitud,
                'longitud'   : m.longitud,
                'capacidad'  : m.capacidad_hilos,
                'libres'     : libres,
                'ocupados'   : ocupados,
                'reservados' : reservados,  # ← Agregado
                'hilos'      : hilos_data,
                'cable_troncal': {
                    'id': m.cable_troncal.id if m.cable_troncal else None,
                    'codigo': m.cable_troncal.codigo if m.cable_troncal else 'Sin asignar',
                    'capacidad': m.cable_troncal.capacidad if m.cable_troncal else 0
                },
                
                # Datos adicionales para análisis
                'ocupacion_porcentaje': round((ocupados / m.capacidad_hilos * 100) if m.capacidad_hilos > 0 else 0, 1),
                'disponibilidad': 'alta' if libres > m.capacidad_hilos * 0.7 else 
                                 'media' if libres > m.capacidad_hilos * 0.3 else 'baja'
            })

    # Retornar datos con proyectos incluidos y filtros disponibles
    return JsonResponse({
        'mufas': data,
        'proyectos_disponibles': list(proyectos_activos),
        'cables_troncales': list(cables_troncales),
        'filtros_aplicados': {
            'cable_troncal': cable_troncal_id,
            'distrito': distrito,
            'tipo': tipo
        }
    }, safe=False)


def obtener_cables(request):
    """
    Devuelve un array JSON con todos los cables troncales,
    indicando código, capacidad y coords de origen/destino.
    """
    data = []
    qs = CableTroncal.objects.prefetch_related('mufas').all()
    
    for c in qs:
        # Obtener mufas conectadas a este cable
        mufas_conectadas = c.mufas.filter(
            latitud__isnull=False, 
            longitud__isnull=False
        )[:2]  # Tomar las primeras 2 como origen y destino
        
        if len(mufas_conectadas) >= 2:
            data.append({
                'codigo'     : c.codigo,
                'capacidad'  : c.capacidad,
                'origen'     : {
                    'codigo': mufas_conectadas[0].codigo,
                    'lat': mufas_conectadas[0].latitud, 
                    'lng': mufas_conectadas[0].longitud
                },
                'destino'    : {
                    'codigo': mufas_conectadas[1].codigo,
                    'lat': mufas_conectadas[1].latitud, 
                    'lng': mufas_conectadas[1].longitud
                },
                'descripcion': c.descripcion or '',
            })
    
    return JsonResponse(data, safe=False)


def obtener_conexiones(request):
    """
    Devuelve un array JSON con todas las conexiones de hilo→hilo,
    incluyendo coordenadas de las múfas de origen y destino.
    """
    data = []
    qs = Conexion.objects.select_related('origen__mufa', 'destino__mufa').all()
    
    for con in qs:
        # Solo incluir conexiones donde ambas mufas tienen coordenadas
        if (con.origen.mufa.latitud and con.origen.mufa.longitud and
            con.destino.mufa.latitud and con.destino.mufa.longitud):
            
            data.append({
                'origen': {
                    'mufa': con.origen.mufa.codigo,
                    'hilo': con.origen.numero,
                    'lat' : con.origen.mufa.latitud,
                    'lng' : con.origen.mufa.longitud,
                },
                'destino': {
                    'mufa': con.destino.mufa.codigo,
                    'hilo': con.destino.numero,
                    'lat' : con.destino.mufa.latitud,
                    'lng' : con.destino.mufa.longitud,
                },
                'observaciones': con.observaciones or '',
            })
    
    return JsonResponse(data, safe=False)


@require_POST
@login_required
@permission_required('mufas.change_hilo', raise_exception=True)
def asignar_hilo(request):
    """
    Recibe JSON { hilo_id: int, proyecto_id: int }
    Marca el hilo como 'ocupado' y actualiza su campo 'uso' con el código del proyecto.
    """
    try:
        payload = json.loads(request.body)
        hilo = get_object_or_404(Hilo, id=payload['hilo_id'])
        
        # Validar que el hilo esté libre
        if hilo.estado != 'libre':
            return HttpResponseBadRequest('El hilo no está libre')
        
        # Obtener el proyecto seleccionado
        proyecto_id = payload.get('proyecto_id')
        if proyecto_id:
            proyecto = get_object_or_404(Proyecto, id=proyecto_id)
            hilo.uso = f"{proyecto.codigo} - {proyecto.nombre_edificio}"
        else:
            # Fallback para uso libre (texto)
            hilo.uso = payload.get('uso', '').strip()
        
        hilo.estado = 'ocupado'
        hilo.save()
        
        return JsonResponse({
            'status': 'ok',
            'message': f'Hilo {hilo.numero} asignado exitosamente'
        })
        
    except json.JSONDecodeError:
        return HttpResponseBadRequest('JSON inválido')
    except Exception as e:
        return HttpResponseBadRequest(str(e))


def obtener_estadisticas_generales(request):
    """
    Nueva vista para obtener estadísticas generales del sistema.
    Útil para el panel de control.
    """
    mufas = Mufa.objects.prefetch_related('hilos').all()
    
    total_mufas = mufas.count()
    total_hilos = sum(mufa.hilos.count() for mufa in mufas)
    
    hilos_libres = 0
    hilos_ocupados = 0
    hilos_reservados = 0
    
    mufas_problematicas = []
    mufas_disponibles = []
    
    for mufa in mufas:
        hilos = mufa.hilos.all()
        libres = sum(1 for h in hilos if h.estado == 'libre')
        ocupados = sum(1 for h in hilos if h.estado == 'ocupado')
        reservados = sum(1 for h in hilos if h.estado == 'reservado')
        
        hilos_libres += libres
        hilos_ocupados += ocupados
        hilos_reservados += reservados
        
        # Clasificar mufas
        total_mufa = hilos.count()
        if total_mufa > 0:
            ocupacion = ocupados / total_mufa
            if ocupacion > 0.8 or libres == 0:
                mufas_problematicas.append({
                    'codigo': mufa.codigo,
                    'ocupacion': round(ocupacion * 100, 1),
                    'libres': libres
                })
            elif ocupacion < 0.5 and libres > 5:
                mufas_disponibles.append({
                    'codigo': mufa.codigo,
                    'libres': libres,
                    'capacidad': total_mufa
                })
    
    return JsonResponse({
        'resumen': {
            'total_mufas': total_mufas,
            'total_hilos': total_hilos,
            'hilos_libres': hilos_libres,
            'hilos_ocupados': hilos_ocupados,
            'hilos_reservados': hilos_reservados,
            'porcentaje_ocupacion': round((hilos_ocupados / total_hilos * 100) if total_hilos > 0 else 0, 1)
        },
        'alertas': {
            'mufas_problematicas': len(mufas_problematicas),
            'mufas_disponibles': len(mufas_disponibles),
        },
        'detalles': {
            'problematicas': mufas_problematicas[:10],  # Top 10
            'disponibles': mufas_disponibles[:10]       # Top 10
        }
    })