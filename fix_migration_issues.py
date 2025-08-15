#!/usr/bin/env python
"""
Script para solucionar problemas de migración
Ejecutar si hay problemas con la base de datos bloqueada
"""
import os
import sqlite3
import sys

def fix_database_lock():
    print("Solucionando problema de base de datos bloqueada...")
    
    db_path = "db.sqlite3"
    
    if os.path.exists(db_path):
        try:
            # Verificar si la base de datos está bloqueada
            conn = sqlite3.connect(db_path, timeout=1)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()
            
            print(f"Base de datos accesible. Tablas encontradas: {len(tables)}")
            for table in tables:
                print(f"   - {table[0]}")
                
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                print("Base de datos bloqueada. Eliminando para recrear...")
                os.remove(db_path)
                print("Base de datos eliminada. Ahora puedes ejecutar las migraciones.")
            else:
                print(f"Error en base de datos: {e}")
        except Exception as e:
            print(f"Error inesperado: {e}")
    else:
        print("Base de datos no existe. Se creara con las migraciones.")

def check_migrations():
    print("\nVerificando archivos de migracion...")
    
    migrations_dir = "mufas/migrations"
    if os.path.exists(migrations_dir):
        migration_files = [f for f in os.listdir(migrations_dir) if f.endswith('.py') and f != '__init__.py']
        print(f"Encontradas {len(migration_files)} migraciones:")
        for migration in migration_files:
            print(f"   - {migration}")
    else:
        print("Directorio de migraciones no encontrado")

def main():
    print("Herramienta de reparacion de migraciones WinFibra")
    print("=" * 50)
    
    fix_database_lock()
    check_migrations()
    
    print("\nPasos siguientes:")
    print("1. python manage.py makemigrations")
    print("2. python manage.py migrate")
    print("3. python manage.py shell < create_demo_slots.py")
    print("4. python manage.py runserver")

if __name__ == "__main__":
    main()