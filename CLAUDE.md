# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
WinFibra is a Django web application for managing fiber optic infrastructure (mufas). It provides a responsive interface optimized for mobile devices to track cables, fiber connections, and project management.

## Development Commands

### Quick Start Options
```bash
# Mobile-optimized demo (recommended for testing)
./demo_responsivo.sh
# Visits: http://localhost:8000/demo_html_responsivo.html

# Full Django development server
./quick_start.sh
# Creates superuser admin/admin123 and loads demo data

# Docker development
./start_docker.sh
```

### Django Management
```bash
# Standard Django commands
python manage.py runserver
python manage.py migrate
python manage.py makemigrations
python manage.py collectstatic

# Create superuser (credentials: admin/admin123 for demo)
python manage.py createsuperuser

# Load demo data
python init_demo_data.py
```

### Database Setup
- Uses SQLite by default
- Demo data includes: 5 projects, 8 mufas in Lima, 192 fiber threads
- Database is recreated fresh on each quick_start.sh run

## Architecture

### Django Apps Structure
- **core/**: Main Django project settings and configuration
- **mufas/**: Fiber infrastructure management (cables, mufas, threads, connections)  
- **proyectos/**: Project management with tracking, tasks, and analytics
- **roles/**: User role management system

### Key Models
- **Mufa**: Fiber junction boxes with geolocation (latitude/longitude)
- **CableTroncal**: Trunk cables with capacity (12-128 threads)
- **Hilo**: Individual fiber threads with status (libre/ocupado/reservado)
- **Conexion**: Fiber connections between threads
- **Proyecto**: Projects with status tracking, budgets, and progress
- **SeguimientoProyecto**: Project change history
- **TareaProyecto**: Project tasks management

### Mobile-First Design
- Responsive breakpoints: 768px (tablets), 480px (mobile)
- Hamburger navigation for mobile
- Touch-friendly 44px minimum button sizes
- Optimized charts and tables for small screens
- Landscape orientation support

## Key URLs
- Dashboard: http://localhost:8000/
- Fiber Map: http://localhost:8000/mufas/mapa/
- Analytics: http://localhost:8000/proyectos/analytics/
- Admin: http://localhost:8000/admin/

## Dependencies
- Django >=5.2.0
- geopy >=2.3.0 (for geolocation)
- Pillow >=10.0.0 (for image handling)
- gunicorn, whitenoise (production)

## Testing Mobile Responsiveness
1. Run demo server
2. Open in browser and press F12
3. Enable Device Toolbar
4. Test with iPhone SE, iPhone 12 Pro, iPad profiles
5. Test portrait/landscape orientations

## Remote Demo with Ngrok
```bash
./ngrok.exe http 8000
```
Use the generated URL to share mobile demos remotely.

## Configuration Notes
- Language: Spanish (es-pe)
- Timezone: America/Lima
- Uses environment variables for production settings
- WhiteNoise middleware for static files
- Security headers configured for production mode