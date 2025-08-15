#!/usr/bin/env python3
"""
Script para crear slots de cables de ejemplo en las mufas existentes
"""
import os
import sys
import django
from datetime import datetime, timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from mufas.models import Mufa, CableTroncal, CableSlot

def create_cable_slots():
    print("🔧 Creando slots de cables para las mufas existentes...")
    
    # Obtener todas las mufas
    mufas = Mufa.objects.all()
    cables_troncales = list(CableTroncal.objects.all())
    
    if not cables_troncales:
        print("❌ No hay cables troncales en la base de datos")
        return
    
    slots_creados = 0
    
    for mufa in mufas:
        print(f"  → Creando slots para mufa {mufa.codigo}")
        
        # Crear slots de ejemplo para cada mufa
        slots_data = [
            {
                'numero_slot': 1,
                'tipo_cable': 'ingreso',
                'cable_troncal': cables_troncales[0],
                'estado': 'ocupado',
                'hilos_utilizados': 24,
                'descripcion': f'Cable principal de ingreso para {mufa.codigo}'
            },
            {
                'numero_slot': 2,
                'tipo_cable': 'salida',
                'cable_troncal': cables_troncales[1] if len(cables_troncales) > 1 else cables_troncales[0],
                'estado': 'ocupado',
                'hilos_utilizados': 12,
                'descripcion': f'Cable de salida hacia siguiente mufa'
            },
            {
                'numero_slot': 3,
                'tipo_cable': 'derivacion',
                'cable_troncal': None,
                'estado': 'libre',
                'hilos_utilizados': 0,
                'descripcion': 'Slot libre para derivación'
            },
            {
                'numero_slot': 4,
                'tipo_cable': 'derivacion',
                'cable_troncal': None,
                'estado': 'reservado',
                'hilos_utilizados': 0,
                'descripcion': 'Slot reservado para futuras derivaciones'
            }
        ]
        
        for slot_data in slots_data:
            slot, created = CableSlot.objects.get_or_create(
                mufa=mufa,
                numero_slot=slot_data['numero_slot'],
                defaults={
                    'tipo_cable': slot_data['tipo_cable'],
                    'cable_troncal': slot_data['cable_troncal'],
                    'estado': slot_data['estado'],
                    'hilos_utilizados': slot_data['hilos_utilizados'],
                    'descripcion': slot_data['descripcion'],
                    'fecha_instalacion': datetime.now(timezone.utc) if slot_data['estado'] == 'ocupado' else None
                }
            )
            
            if created:
                slots_creados += 1
                print(f"    ✓ Slot {slot_data['numero_slot']} - {slot_data['tipo_cable']}")
    
    print(f"🎉 Se crearon {slots_creados} slots de cables exitosamente!")
    print(f"📊 Total de slots en el sistema: {CableSlot.objects.count()}")

if __name__ == '__main__':
    create_cable_slots()