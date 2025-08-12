#!/bin/bash

echo "WinFibra - Iniciando contenedor..."

# Aplicar migraciones
python manage.py makemigrations --noinput || true
python manage.py migrate --noinput || true

# Archivos estáticos
python manage.py collectstatic --noinput || true

# Crear superusuario admin/admin123
python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@winfibra.com', 'admin123')
    print('Usuario admin creado')
else:
    print('Usuario admin existe')
" || true

# Datos demo
python init_demo_data.py || true

echo ""
echo "Listo! URLs:"
echo "   http://localhost:8000"
echo "   http://localhost:8000/mufas/mapa/"
echo "   http://localhost:8000/proyectos/analytics/"
echo ""
echo "admin / admin123"
echo ""

# Iniciar servidor
exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120 --log-level info