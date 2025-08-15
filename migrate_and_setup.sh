#!/bin/bash

# Script simple y directo para configurar WinFibra con slots de cables
echo "============================================================"
echo "WINFIBRA - CONFIGURACION DE SLOTS DE CABLES"
echo "============================================================"

# Detectar Python
if [ -f "C:/Users/elray/AppData/Local/Programs/Python/Python312/python.exe" ]; then
    PYTHON_CMD="C:/Users/elray/AppData/Local/Programs/Python/Python312/python.exe"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "ERROR: Python no encontrado"
    exit 1
fi

echo "Python detectado: $("$PYTHON_CMD" --version)"

# Verificar Django
"$PYTHON_CMD" -c "import django; print('Django', django.get_version(), 'OK')" || {
    echo "Instalando Django..."
    "$PYTHON_CMD" -m pip install Django==5.2.5 geopy Pillow psutil
}

# Limpiar completamente
echo "Limpiando archivos previos..."
rm -f db.sqlite3* 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Esperar un momento para asegurar que no hay procesos activos
sleep 2

# Crear migraciones
echo "Creando migraciones..."
"$PYTHON_CMD" manage.py makemigrations --noinput

# Aplicar migraciones
echo "Aplicando migraciones..."
"$PYTHON_CMD" manage.py migrate --noinput

# Verificar que la base de datos se creó
if [ ! -f "db.sqlite3" ]; then
    echo "ERROR: La base de datos no se creó correctamente"
    exit 1
fi

echo "Base de datos creada exitosamente"

# Crear superusuario
echo "Creando superusuario admin..."
"$PYTHON_CMD" -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@winfibra.com', 'admin123')
    print('Superusuario creado: admin/admin123')
else:
    print('Superusuario ya existe')
"

# Ejecutar script de datos básicos
echo "Creando datos de demostración básicos..."
if [ -f "init_demo_data.py" ]; then
    "$PYTHON_CMD" manage.py shell < init_demo_data.py
    echo "Datos básicos creados"
else
    echo "ADVERTENCIA: init_demo_data.py no encontrado"
fi

# Ejecutar script de slots
echo "Creando slots de cables..."
if [ -f "create_demo_slots.py" ]; then
    "$PYTHON_CMD" manage.py shell < create_demo_slots.py
    echo "Slots de cables creados"
else
    echo "ADVERTENCIA: create_demo_slots.py no encontrado"
fi

# Verificar datos
echo "Verificando datos..."
"$PYTHON_CMD" -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from mufas.models import Mufa, CableSlot
from proyectos.models import Proyecto

mufas_count = Mufa.objects.count()
slots_count = CableSlot.objects.count()
projects_count = Proyecto.objects.count()

print(f'Mufas: {mufas_count}')
print(f'Slots de cables: {slots_count}')
print(f'Proyectos: {projects_count}')

if mufas_count > 0 and slots_count > 0:
    print('ÉXITO: Datos creados correctamente')
else:
    print('ADVERTENCIA: Faltan algunos datos')
"

echo "============================================================"
echo "CONFIGURACIÓN COMPLETADA"
echo "============================================================"
echo ""
echo "PRÓXIMOS PASOS:"
echo "1. Ejecutar servidor: python manage.py runserver"
echo "2. Abrir: http://localhost:8000/mufas/mapa/"
echo "3. Hacer clic en cualquier mufa del mapa"
echo "4. Usar botón 'Ver Slots de Cables'"
echo ""
echo "Admin: http://localhost:8000/admin/"
echo "Usuario: admin / Contraseña: admin123"
echo ""