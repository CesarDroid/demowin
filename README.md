# 🚀 WinFibra - Sistema de Gestión de Fibra Óptica

Sistema profesional de gestión de mufas con **interfaz completamente responsive** para dispositivos móviles.

## ⚡ Inicio Rápido

### 📱 Demo Responsivo (RECOMENDADO para pruebas móviles)
```bash
./demo_responsivo.sh
```
Luego visita: http://localhost:8000/demo_html_responsivo.html

### 🗃️ Servidor Django Completo
```bash
./quick_start.sh
```

### 🐳 Docker
```bash
./start_docker.sh
```

## 📱 URLs Demo Responsivo

- **🎯 Demo Principal**: http://localhost:8000/demo_html_responsivo.html

## 📱 URLs Sistema Completo

- **🏠 Dashboard**: http://localhost:8000
- **🗺️ Mapa de Mufas**: http://localhost:8000/mufas/mapa/
- **📊 Analytics**: http://localhost:8000/proyectos/analytics/
- **🔐 Admin**: http://localhost:8000/admin/

**Credenciales**: `admin` / `admin123`

## 🌐 Demo Remoto con Ngrok

```bash
./ngrok.exe http 8000
```

## 📱 Características Móviles

✅ **Completamente Responsive**
- Navegación hamburger para móviles
- Panel de mufas minimizable
- Tablas con scroll horizontal
- Gráficos optimizados para pantallas pequeñas
- Botones táctiles de 44px mínimo
- Formularios mobile-first

✅ **Breakpoints**
- 768px (tablets)
- 480px (móviles)
- Modo landscape

## 🔧 Probar Responsividad

1. Abrir cualquier URL
2. **F12** → Developer Tools
3. **Device Toolbar** (ícono móvil)
4. Probar: iPhone SE, iPhone 12 Pro, iPad

## 📋 Datos Demo

- 5 proyectos de demostración
- 8 mufas en Lima con coordenadas reales
- 192 hilos (70% libres, 25% ocupados, 5% reservados)

## 🛠️ Comandos Útiles

```bash
# Ver logs Docker
docker-compose logs -f

# Reiniciar Docker
docker-compose restart

# Limpiar Docker
docker-compose down -v
```

---

🎯 **Listo para impresionar al cliente con una experiencia móvil profesional**