#!/usr/bin/env python
"""
Setup Clean Database - WinFibra
Script para configurar una base de datos limpia siguiendo buenas prácticas
"""
import os
import sys
import subprocess
import time
import sqlite3
import psutil
from pathlib import Path

def log_info(message):
    """Log con formato consistente"""
    print(f"[INFO] {message}")

def log_success(message):
    """Log de éxito"""
    print(f"[SUCCESS] {message}")

def log_error(message):
    """Log de error"""
    print(f"[ERROR] {message}")

def log_warning(message):
    """Log de advertencia"""
    print(f"[WARNING] {message}")

def find_python_processes():
    """Encuentra procesos Python relacionados con Django/manage.py"""
    python_processes = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = proc.info['cmdline'] or []
                    # Buscar procesos que ejecuten manage.py o runserver
                    if any('manage.py' in arg or 'runserver' in arg or 'django' in arg.lower() 
                           for arg in cmdline if isinstance(arg, str)):
                        python_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': ' '.join(cmdline)
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    except Exception as e:
        log_warning(f"No se pudo enumerar procesos: {e}")
    
    return python_processes

def terminate_python_processes():
    """Termina procesos Python relacionados con Django de forma segura"""
    log_info("Buscando procesos Python que puedan bloquear la DB...")
    
    processes = find_python_processes()
    
    if not processes:
        log_success("No se encontraron procesos Python conflictivos")
        return True
    
    log_info(f"Encontrados {len(processes)} procesos Python:")
    for proc in processes:
        log_info(f"  PID {proc['pid']}: {proc['cmdline'][:80]}...")
    
    # Intentar terminación elegante primero
    for proc in processes:
        try:
            p = psutil.Process(proc['pid'])
            log_info(f"Terminando proceso PID {proc['pid']} elegantemente...")
            p.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            log_warning(f"No se pudo terminar PID {proc['pid']}: {e}")
    
    # Esperar a que terminen
    log_info("Esperando terminación de procesos...")
    time.sleep(3)
    
    # Verificar si algunos procesos siguen vivos y forzar terminación
    remaining = find_python_processes()
    if remaining:
        log_warning(f"Forzando terminación de {len(remaining)} procesos restantes...")
        for proc in remaining:
            try:
                p = psutil.Process(proc['pid'])
                p.kill()
                log_info(f"Proceso PID {proc['pid']} terminado forzadamente")
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                log_error(f"No se pudo terminar forzadamente PID {proc['pid']}: {e}")
    
    time.sleep(2)
    final_check = find_python_processes()
    if final_check:
        log_error(f"Aún quedan {len(final_check)} procesos activos")
        return False
    else:
        log_success("Todos los procesos Python terminados correctamente")
        return True

def clean_database_files():
    """Limpia archivos de base de datos y cache"""
    log_info("Limpiando archivos de base de datos y cache...")
    
    files_to_remove = [
        'db.sqlite3',
        'db.sqlite3.backup',
        'db.sqlite3-journal',
        'db.sqlite3-wal',
        'db.sqlite3-shm'
    ]
    
    removed_count = 0
    for file_name in files_to_remove:
        file_path = Path(file_name)
        if file_path.exists():
            try:
                file_path.unlink()
                log_success(f"Eliminado: {file_name}")
                removed_count += 1
            except OSError as e:
                log_error(f"No se pudo eliminar {file_name}: {e}")
        else:
            log_info(f"No existe: {file_name}")
    
    # Limpiar cache de Python
    cache_dirs = ['__pycache__', '.pytest_cache']
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name in cache_dirs:
                cache_path = Path(root) / dir_name
                try:
                    import shutil
                    shutil.rmtree(cache_path)
                    log_success(f"Cache eliminado: {cache_path}")
                    removed_count += 1
                except Exception as e:
                    log_warning(f"No se pudo eliminar cache {cache_path}: {e}")
    
    log_success(f"Limpieza completada. {removed_count} elementos eliminados")
    return True

def verify_migrations():
    """Verifica la integridad de las migraciones"""
    log_info("Verificando integridad de migraciones...")
    
    migration_dirs = ['mufas/migrations', 'proyectos/migrations', 'roles/migrations']
    
    for migration_dir in migration_dirs:
        migration_path = Path(migration_dir)
        if not migration_path.exists():
            log_error(f"Directorio de migraciones no existe: {migration_dir}")
            return False
        
        migration_files = list(migration_path.glob('*.py'))
        migration_files = [f for f in migration_files if f.name != '__init__.py']
        
        if not migration_files:
            log_warning(f"No hay archivos de migración en {migration_dir}")
        else:
            log_success(f"{migration_dir}: {len(migration_files)} migraciones encontradas")
    
    # Verificar sintaxis de models.py
    model_files = ['mufas/models.py', 'proyectos/models.py', 'roles/models.py']
    for model_file in model_files:
        model_path = Path(model_file)
        if model_path.exists():
            try:
                with open(model_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Verificación básica de sintaxis
                    compile(content, model_file, 'exec')
                log_success(f"Sintaxis correcta: {model_file}")
            except SyntaxError as e:
                log_error(f"Error de sintaxis en {model_file}: {e}")
                return False
            except Exception as e:
                log_warning(f"No se pudo verificar {model_file}: {e}")
    
    return True

def get_python_command():
    """Obtiene el comando Python correcto para usar"""
    python_paths = [
        "C:/Users/elray/AppData/Local/Programs/Python/Python312/python.exe",
        "python",
        "python3",
        "py"
    ]
    
    for python_path in python_paths:
        try:
            result = subprocess.run(
                [python_path, "--version"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode == 0:
                log_success(f"Python encontrado: {python_path} ({result.stdout.strip()})")
                return python_path
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            continue
    
    log_error("No se encontró un comando Python válido")
    return None

def run_migrations(python_cmd):
    """Ejecuta las migraciones de Django"""
    log_info("Ejecutando migraciones de Django...")
    
    commands = [
        ([python_cmd, "manage.py", "makemigrations"], "Generando migraciones"),
        ([python_cmd, "manage.py", "migrate"], "Aplicando migraciones"),
    ]
    
    for cmd, description in commands:
        log_info(f"{description}...")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd='.'
            )
            
            if result.returncode == 0:
                log_success(f"{description} completado")
                if result.stdout.strip():
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            log_info(f"  {line}")
            else:
                log_error(f"{description} falló")
                if result.stderr:
                    for line in result.stderr.strip().split('\n'):
                        if line.strip():
                            log_error(f"  {line}")
                return False
                
        except subprocess.TimeoutExpired:
            log_error(f"{description} expiró (timeout)")
            return False
        except Exception as e:
            log_error(f"{description} error: {e}")
            return False
    
    return True

def create_demo_data(python_cmd):
    """Crea datos de demostración"""
    log_info("Creando datos de demostración...")
    
    # Primero crear datos básicos
    init_script = Path("init_demo_data.py")
    if init_script.exists():
        log_info("Ejecutando script de datos básicos...")
        try:
            with open(init_script, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            result = subprocess.run(
                [python_cmd, "manage.py", "shell"],
                input=script_content,
                text=True,
                capture_output=True,
                timeout=60
            )
            
            if result.returncode == 0:
                log_success("Datos básicos creados")
                if result.stdout.strip():
                    for line in result.stdout.strip().split('\n')[-5:]:  # Últimas 5 líneas
                        log_info(f"  {line}")
            else:
                log_warning("Advertencias en datos básicos:")
                if result.stderr:
                    for line in result.stderr.strip().split('\n')[-3:]:  # Últimas 3 líneas
                        log_warning(f"  {line}")
        
        except Exception as e:
            log_error(f"Error creando datos básicos: {e}")
    
    # Luego crear datos de slots
    slots_script = Path("create_demo_slots.py")
    if slots_script.exists():
        log_info("Ejecutando script de slots de cables...")
        try:
            with open(slots_script, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            result = subprocess.run(
                [python_cmd, "manage.py", "shell"],
                input=script_content,
                text=True,
                capture_output=True,
                timeout=60
            )
            
            if result.returncode == 0:
                log_success("Datos de slots creados")
                if result.stdout.strip():
                    for line in result.stdout.strip().split('\n')[-5:]:  # Últimas 5 líneas
                        log_info(f"  {line}")
            else:
                log_error("Error creando datos de slots:")
                if result.stderr:
                    for line in result.stderr.strip().split('\n')[-3:]:
                        log_error(f"  {line}")
                return False
        
        except Exception as e:
            log_error(f"Error ejecutando script de slots: {e}")
            return False
    
    return True

def verify_database():
    """Verifica que la base de datos esté funcionando correctamente"""
    log_info("Verificando base de datos...")
    
    db_path = "db.sqlite3"
    if not os.path.exists(db_path):
        log_error("Base de datos no fue creada")
        return False
    
    try:
        conn = sqlite3.connect(db_path, timeout=5)
        cursor = conn.cursor()
        
        # Verificar tablas principales
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        expected_tables = ['mufas_mufa', 'mufas_cableslot', 'mufas_hilo', 'mufas_conexion', 'proyectos_proyecto']
        found_tables = [t for t in expected_tables if t in table_names]
        
        log_success(f"Base de datos verificada. Tablas encontradas: {len(table_names)}")
        log_info(f"Tablas clave encontradas: {len(found_tables)}/{len(expected_tables)}")
        
        # Verificar datos de slots
        cursor.execute("SELECT COUNT(*) FROM mufas_cableslot;")
        slot_count = cursor.fetchone()[0]
        log_info(f"Slots de cables en DB: {slot_count}")
        
        cursor.execute("SELECT COUNT(*) FROM mufas_mufa;")
        mufa_count = cursor.fetchone()[0]
        log_info(f"Mufas en DB: {mufa_count}")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        log_error(f"Error verificando base de datos: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 60)
    print("SETUP CLEAN DATABASE - WINFIBRA")
    print("=" * 60)
    
    # Paso 1: Terminar procesos
    log_info("PASO 1: Terminando procesos Python conflictivos...")
    if not terminate_python_processes():
        log_error("No se pudieron terminar todos los procesos")
        return False
    
    # Paso 2: Limpiar archivos
    log_info("PASO 2: Limpiando archivos de base de datos y cache...")
    if not clean_database_files():
        log_error("Error en limpieza de archivos")
        return False
    
    # Paso 3: Verificar migraciones
    log_info("PASO 3: Verificando integridad de migraciones...")
    if not verify_migrations():
        log_error("Error en verificación de migraciones")
        return False
    
    # Paso 4: Obtener comando Python
    python_cmd = get_python_command()
    if not python_cmd:
        return False
    
    # Paso 5: Ejecutar migraciones
    log_info("PASO 5: Ejecutando migraciones...")
    if not run_migrations(python_cmd):
        log_error("Error en migraciones")
        return False
    
    # Paso 6: Crear datos demo
    log_info("PASO 6: Creando datos de demostración...")
    if not create_demo_data(python_cmd):
        log_error("Error creando datos demo")
        return False
    
    # Paso 7: Verificar base de datos
    log_info("PASO 7: Verificación final...")
    if not verify_database():
        log_error("Error en verificación final")
        return False
    
    print("=" * 60)
    log_success("SETUP COMPLETADO EXITOSAMENTE")
    print("=" * 60)
    print()
    log_info("PRÓXIMOS PASOS:")
    log_info("1. Ejecutar: python manage.py runserver")
    log_info("2. Abrir: http://localhost:8000/mufas/mapa/")
    log_info("3. Hacer clic en cualquier mufa")
    log_info("4. Usar botón 'Ver Slots de Cables'")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        log_info("Operación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        log_error(f"Error inesperado: {e}")
        sys.exit(1)