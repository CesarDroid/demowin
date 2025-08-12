#!/usr/bin/env python
"""
Script para inicializar datos de demostración para WinFibra
Ejecutar: python manage.py shell < init_demo_data.py
"""
import os
import django
from django.contrib.auth.models import User
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from mufas.models import Mufa, Hilo
from proyectos.models import Proyecto

def create_demo_data():
    print("🚀 Inicializando datos demo para WinFibra...")
    
    # Crear superusuario demo
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@winfibra.com', 'admin123')
        print('✅ Superusuario creado: admin/admin123')
    else:
        print('ℹ️  Superusuario ya existe')

    # Crear algunos proyectos demo
    proyectos_demo = [
        {'codigo': 'PRY-001', 'nombre': 'Torre Empresarial Norte', 'distrito': 'Miraflores', 'estado': 'en_construccion'},
        {'codigo': 'PRY-002', 'nombre': 'Residencial Las Flores', 'distrito': 'San Isidro', 'estado': 'planificacion'},
        {'codigo': 'PRY-003', 'nombre': 'Centro Comercial Plaza', 'distrito': 'Surco', 'estado': 'aprobado'},
        {'codigo': 'PRY-004', 'nombre': 'Edificio Los Jardines', 'distrito': 'La Molina', 'estado': 'en_construccion'},
        {'codigo': 'PRY-005', 'nombre': 'Condominio Vista Mar', 'distrito': 'Barranco', 'estado': 'planificacion'},
    ]

    for p_data in proyectos_demo:
        if not Proyecto.objects.filter(codigo=p_data['codigo']).exists():
            Proyecto.objects.create(
                codigo=p_data['codigo'],
                nombre_edificio=p_data['nombre'],
                direccion=f'Av. Demo {random.randint(100, 999)}',
                departamento='Lima',
                distrito=p_data['distrito'],
                latitud=-12.0 + random.uniform(-0.1, 0.1),
                longitud=-77.0 + random.uniform(-0.1, 0.1),
                cantidad_pisos=random.randint(5, 20),
                cantidad_departamentos=random.randint(10, 50),
                estado=p_data['estado'],
                progreso_porcentaje=random.randint(10, 85),
                presupuesto_estimado=random.randint(50000, 500000)
            )
            print(f'✅ Proyecto creado: {p_data["codigo"]} - {p_data["nombre"]}')

    # Crear mufas demo en Lima
    mufas_demo = [
        {'codigo': 'MUFA-LIM-001', 'tipo': 'troncal', 'distrito': 'Miraflores', 'lat': -12.120, 'lng': -77.030},
        {'codigo': 'MUFA-LIM-002', 'tipo': 'derivacion', 'distrito': 'San Isidro', 'lat': -12.100, 'lng': -77.035},
        {'codigo': 'MUFA-LIM-003', 'tipo': 'final', 'distrito': 'Surco', 'lat': -12.110, 'lng': -77.025},
        {'codigo': 'MUFA-LIM-004', 'tipo': 'troncal', 'distrito': 'La Molina', 'lat': -12.080, 'lng': -77.020},
        {'codigo': 'MUFA-LIM-005', 'tipo': 'derivacion', 'distrito': 'Barranco', 'lat': -12.140, 'lng': -77.025},
        {'codigo': 'MUFA-LIM-006', 'tipo': 'final', 'distrito': 'Jesús María', 'lat': -12.075, 'lng': -77.045},
        {'codigo': 'MUFA-LIM-007', 'tipo': 'troncal', 'distrito': 'Lince', 'lat': -12.090, 'lng': -77.040},
        {'codigo': 'MUFA-LIM-008', 'tipo': 'derivacion', 'distrito': 'Magdalena', 'lat': -12.095, 'lng': -77.055},
    ]

    proyectos_disponibles = list(Proyecto.objects.all())

    for m_data in mufas_demo:
        if not Mufa.objects.filter(codigo=m_data['codigo']).exists():
            mufa = Mufa.objects.create(
                codigo=m_data['codigo'],
                tipo=m_data['tipo'],
                descripcion=f'Mufa de {m_data["tipo"]} ubicada en {m_data["distrito"]}',
                ubicacion=f'Intersección Principal - {m_data["distrito"]}',
                distrito=m_data['distrito'],
                latitud=m_data['lat'],
                longitud=m_data['lng'],
                capacidad_hilos=24
            )
            
            # Crear hilos para cada mufa
            for i in range(1, 25):
                # Determinar estado (70% libre, 25% ocupado, 5% reservado)
                rand = random.random()
                if rand < 0.70:
                    estado = 'libre'
                    uso = ''
                elif rand < 0.95:
                    estado = 'ocupado'
                    # Asignar a un proyecto random
                    proyecto = random.choice(proyectos_disponibles)
                    uso = f'{proyecto.codigo} - {proyecto.nombre_edificio}'
                else:
                    estado = 'reservado'
                    uso = 'Reservado para mantenimiento'
                
                Hilo.objects.create(
                    mufa=mufa,
                    numero=i,
                    estado=estado,
                    uso=uso,
                    splitter=f'SP-{i:02d}',
                    destino=f'Terminal-{i}' if estado == 'ocupado' else ''
                )
            
            print(f'✅ Mufa creada: {m_data["codigo"]} con 24 hilos en {m_data["distrito"]}')

    print("\n🎉 ¡Datos demo creados exitosamente!")
    print("\n📊 Resumen:")
    print(f"   • Proyectos: {Proyecto.objects.count()}")
    print(f"   • Mufas: {Mufa.objects.count()}")
    print(f"   • Hilos: {Hilo.objects.count()}")
    print(f"   • Hilos libres: {Hilo.objects.filter(estado='libre').count()}")
    print(f"   • Hilos ocupados: {Hilo.objects.filter(estado='ocupado').count()}")
    print(f"   • Hilos reservados: {Hilo.objects.filter(estado='reservado').count()}")
    
    print("\n🔑 Credenciales de acceso:")
    print("   Usuario: admin")
    print("   Contraseña: admin123")
    print("   URL Admin: http://localhost:8000/admin/")
    print("   URL Principal: http://localhost:8000/")

if __name__ == "__main__":
    create_demo_data()