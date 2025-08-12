#!/usr/bin/env python
"""
Script para iniciar el servidor de desarrollo de WinFibra
"""
import os
import sys
import subprocess
from pathlib import Path


def print_banner():
    """Imprime el banner de WinFibra"""
    print("""
🌐 ================================= 🌐
   WINFIBRA - GESTIÓN FIBRA ÓPTICA
🌐 ================================= 🌐
""")


def check_dependencies():
    """Verifica las dependencias necesarias"""
    try:
        import django
        print(f"✅ Django {django.get_version()} instalado")
        return True
    except ImportError:
        print("❌ Django no instalado.")
        print("💡 Ejecuta: pip install -r requirements.txt")
        return False


def setup_database_if_needed():
    """Configura la base de datos si no existe"""
    if not Path("db.sqlite3").exists():
        print("📋 Configurando base de datos...")
        try:
            result = subprocess.run([sys.executable, "setup_database.py"], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error configurando base de datos: {e}")
            return False
    return True


def show_info():
    """Muestra la información del sistema"""
    print("""
📱 URLs del Sistema:
🏠 Dashboard:     http://127.0.0.1:8000/
📋 Proyectos:     http://127.0.0.1:8000/proyectos/
🗺️  Mufas:        http://127.0.0.1:8000/mufas/mapa/
⚙️  Admin:        http://127.0.0.1:8000/admin/

👤 Usuario: admin
🔐 Contraseña: admin123

🚀 Iniciando servidor...
""")


def main():
    """Función principal"""
    print_banner()
    
    # Verificar dependencias
    if not check_dependencies():
        return 1
    
    # Configurar base de datos
    if not setup_database_if_needed():
        return 1
    
    # Mostrar información
    show_info()
    
    # Iniciar servidor
    try:
        subprocess.run([sys.executable, "manage.py", "runserver"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error iniciando servidor: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido")
        return 0
    
    return 0


if __name__ == "__main__":
    sys.exit(main())