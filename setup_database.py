#!/usr/bin/env python
"""
Script para configurar la base de datos inicial de WinFibra
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

django.setup()

from django.core.management import execute_from_command_line
from django.contrib.auth.models import User


def setup_database():
    """Configura la base de datos inicial con migraciones y superusuario"""
    print("🚀 Configurando base de datos de WinFibra...")
    
    try:
        # Crear migraciones y aplicarlas
        print("📋 Aplicando migraciones...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        # Crear superusuario si no existe
        print("👤 Configurando usuario administrador...")
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@winfibra.com',
                password='admin123'
            )
            print("✅ Superusuario creado: admin / admin123")
        else:
            print("✅ Superusuario ya existe")
        
        print("🎉 ¡Base de datos configurada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error configurando base de datos: {e}")
        sys.exit(1)


if __name__ == '__main__':
    setup_database()