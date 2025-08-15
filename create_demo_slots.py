#!/usr/bin/env python
"""
Script para crear datos demo de slots de cables
Ejecutar: python manage.py shell < create_demo_slots.py
"""
import os
import django
import random
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from mufas.models import Mufa, CableTroncal, CableSlot

def create_demo_slots():
    print("🚀 Creando datos demo de slots de cables...")
    
    # Obtener todas las mufas y cables troncales
    mufas = Mufa.objects.all()
    cables = list(CableTroncal.objects.all())
    
    if not mufas.exists():
        print("❌ No hay mufas en la base de datos. Ejecuta primero init_demo_data.py")
        return
    
    if not cables:
        print("ℹ️  No hay cables troncales. Creando algunos cables de ejemplo...")
        cables = []
        cables_demo = [
            {'codigo': 'CT-001', 'descripcion': 'Cable Troncal Principal Norte', 'capacidad': 48},
            {'codigo': 'CT-002', 'descripcion': 'Cable Troncal Principal Sur', 'capacidad': 96},
            {'codigo': 'CT-003', 'descripcion': 'Cable Troncal Derivación Este', 'capacidad': 24},
            {'codigo': 'CT-004', 'descripcion': 'Cable Troncal Derivación Oeste', 'capacidad': 64},
            {'codigo': 'CT-005', 'descripcion': 'Cable Troncal Secundario Centro', 'capacidad': 32},
        ]
        
        for cable_data in cables_demo:
            cable = CableTroncal.objects.create(**cable_data)
            cables.append(cable)
            print(f'✅ Cable creado: {cable.codigo}')
    
    # Crear slots para cada mufa
    slots_creados = 0
    
    for mufa in mufas:
        # Determinar cuántos slots crear según el tipo de mufa
        if mufa.tipo == 'troncal':
            num_slots = random.randint(4, 8)  # Mufas troncales tienen más slots
        elif mufa.tipo == 'derivacion':
            num_slots = random.randint(2, 6)
        else:  # final
            num_slots = random.randint(1, 4)
        
        # Crear slots con diferentes tipos de cable
        for i in range(1, num_slots + 1):
            # Determinar tipo de cable basado en la posición y tipo de mufa
            if mufa.tipo == 'troncal':
                if i <= 2:
                    tipo_cable = 'ingreso' if i == 1 else 'salida'
                else:
                    tipo_cable = 'derivacion'
            elif mufa.tipo == 'derivacion':
                if i == 1:
                    tipo_cable = 'ingreso'
                elif i == 2:
                    tipo_cable = 'salida'  
                else:
                    tipo_cable = 'derivacion'
            else:  # final
                tipo_cable = 'ingreso' if i == 1 else 'derivacion'
            
            # Seleccionar cable troncal apropiado
            cable_troncal = random.choice(cables)
            
            # Determinar estado y utilización
            estado_probabilidad = random.random()
            if estado_probabilidad < 0.65:
                estado = 'ocupado'
                hilos_utilizados = random.randint(
                    cable_troncal.capacidad // 4, 
                    min(cable_troncal.capacidad, mufa.capacidad_hilos)
                )
            elif estado_probabilidad < 0.85:
                estado = 'libre'
                hilos_utilizados = 0
            elif estado_probabilidad < 0.95:
                estado = 'reservado'
                hilos_utilizados = random.randint(0, cable_troncal.capacidad // 8)
            else:
                estado = 'fuera_servicio'
                hilos_utilizados = 0
            
            # Descripción basada en el tipo y estado
            descripciones = {
                'ingreso': [
                    'Conexión desde central telefónica',
                    'Enlace principal de entrada',
                    'Fibra troncal de acceso',
                    'Conexión upstream primaria'
                ],
                'salida': [
                    'Distribución hacia zona residencial',
                    'Enlace a mufa secundaria',
                    'Conexión downstream principal',
                    'Salida hacia edificios comerciales'
                ],
                'derivacion': [
                    'Derivación a edificio específico',
                    'Conexión lateral zona residencial',
                    'Branch hacia torres empresariales',
                    'Derivación para servicios especiales'
                ]
            }
            
            descripcion = random.choice(descripciones[tipo_cable])
            
            # Fecha de instalación (últimos 2 años)
            fecha_instalacion = datetime.now() - timedelta(
                days=random.randint(30, 730)
            )
            
            # Verificar que no exista ya un slot con el mismo número
            if not CableSlot.objects.filter(mufa=mufa, numero_slot=i).exists():
                slot = CableSlot.objects.create(
                    mufa=mufa,
                    cable_troncal=cable_troncal,
                    tipo_cable=tipo_cable,
                    numero_slot=i,
                    estado=estado,
                    descripcion=descripcion,
                    hilos_utilizados=hilos_utilizados,
                    fecha_instalacion=fecha_instalacion
                )
                slots_creados += 1
                
                print(f'✅ Slot creado: {mufa.codigo} - Slot {i} ({tipo_cable}) - {estado}')
    
    print(f"\n🎉 Proceso completado!")
    print(f"   📊 {slots_creados} slots de cables creados")
    print(f"   📡 {len(cables)} cables troncales disponibles")
    print(f"   🏢 {mufas.count()} mufas con slots configurados")
    
    # Mostrar estadísticas
    total_slots = CableSlot.objects.count()
    slots_ocupados = CableSlot.objects.filter(estado='ocupado').count()
    slots_libres = CableSlot.objects.filter(estado='libre').count()
    slots_reservados = CableSlot.objects.filter(estado='reservado').count()
    
    print(f"\n📈 Estadísticas finales:")
    print(f"   Total slots: {total_slots}")
    print(f"   Ocupados: {slots_ocupados}")
    print(f"   Libres: {slots_libres}")
    print(f"   Reservados: {slots_reservados}")


if __name__ == '__main__':
    create_demo_slots()