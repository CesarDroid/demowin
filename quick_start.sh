#!/bin/bash

echo "🚀 WinFibra - Servidor de Desarrollo"
echo "==================================="

# Detectar Python disponible
if command -v python3.12 &> /dev/null; then
    PYTHON_CMD="python3.12"
elif [ -f "C:/Users/elray/AppData/Local/Programs/Python/Python312/python.exe" ]; then
    PYTHON_CMD="C:/Users/elray/AppData/Local/Programs/Python/Python312/python.exe"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python no encontrado"
    exit 1
fi

echo "🐍 Usando: $("$PYTHON_CMD" --version)"

# Verificar Django
"$PYTHON_CMD" -c "import django; print('Django', django.get_version(), 'OK')" || {
    echo "Instalando Django..."
    "$PYTHON_CMD" -m pip install Django==5.2.5 geopy Pillow python-decouple whitenoise
}

# Configurar base de datos limpia
echo "📊 Configurando base de datos..."

# Terminar procesos previos si existen
taskkill //F //IM python.exe 2>/dev/null || true
sleep 1

# Crear nueva base de datos limpia
if [ -f "db.sqlite3" ]; then
    echo "🔄 Renovando base de datos..."
    rm -f db.sqlite3 2>/dev/null || mv db.sqlite3 "db_old_$(date +%s).sqlite3" 2>/dev/null || true
fi

# Aplicar migraciones
echo "🔄 Aplicando migraciones..."
"$PYTHON_CMD" manage.py makemigrations --noinput 2>/dev/null || true
"$PYTHON_CMD" manage.py migrate --noinput

# Inicializar sistema de roles
echo "🏢 Inicializando sistema de roles y áreas..."
"$PYTHON_CMD" manage.py init_roles 2>/dev/null || echo "Sistema de roles inicializado"

# Crear superusuario
echo "👤 Creando usuario admin..."
"$PYTHON_CMD" -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@winfibra.com', 'admin123')
    print('Usuario admin creado')
else:
    print('Usuario admin ya existe')
" 2>/dev/null || echo "Usuario sera creado automaticamente"

# Datos demo
echo "📋 Inicializando datos demo..."
"$PYTHON_CMD" init_demo_data.py 2>/dev/null || echo "Datos demo opcionales no cargados"

echo ""
echo "📱 URLs MÓVILES RESPONSIVE:"
echo "   🏠 Dashboard: http://localhost:8001"
echo "   🗺️  Mapa: http://localhost:8001/mufas/mapa/"
echo "   📊 Analytics: http://localhost:8001/proyectos/analytics/"
echo "   🔐 Control Center: http://localhost:8001/control/"
echo "   🛡️  Management: http://localhost:8001/management/"
echo ""
echo "🔑 Login: admin / admin123 (Administrador del Sistema)"
echo ""
echo "🏢 SISTEMA DE ROLES CONFIGURADO:"
echo "   📋 Área Comercial: Crear proyectos"
echo "   🎯 Área Planificación: Asignar hilos"
echo "   🔨 Área Construcción: Ver proyectos y mufas"
echo "   🛡️  Admin (solo superusuarios): Acceso completo"
echo ""
echo "👥 CREAR USUARIOS: /admin/auth/user/"
echo "🌐 Para ngrok: ./ngrok.exe http 8001"
echo ""
echo "📱 PRUEBA MÓVIL: F12 → Device Toolbar → iPhone/iPad"
echo ""

# Iniciar servidor
echo "🚀 Iniciando servidor..."
"$PYTHON_CMD" manage.py runserver 0.0.0.0:8001