#!/bin/bash

echo "🐳 WinFibra - Docker"
echo "=================="

# Verificar que Docker esté corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está corriendo. Inicia Docker Desktop primero."
    exit 1
fi

# Limpiar contenedores previos
echo "🧹 Limpiando contenedores anteriores..."
docker-compose down -v 2>/dev/null || true

# Verificar archivos necesarios
if [ ! -f "entrypoint.sh" ]; then
    echo "❌ entrypoint.sh no encontrado"
    exit 1
fi

# Construir e iniciar
echo "🔨 Construyendo e iniciando..."
if docker-compose up --build -d; then
    echo "✅ Contenedores iniciados"
else
    echo "❌ Error al construir contenedores"
    echo "📋 Ver errores: docker-compose logs"
    exit 1
fi

# Esperar y verificar
echo "⏳ Esperando inicio (90s)..."
for i in {1..45}; do
    if curl -s http://localhost:8001/ > /dev/null 2>&1; then
        echo ""
        echo "🎉 ¡WinFibra Docker listo!"
        echo ""
        echo "📱 URLs:"
        echo "   🏠 http://localhost:8001"
        echo "   🗺️  http://localhost:8001/mufas/mapa/"
        echo "   📊 http://localhost:8001/proyectos/analytics/"
        echo "   🔐 http://localhost:8001/admin/"
        echo ""
        echo "🔑 admin / admin123"
        echo "🌐 Para ngrok: ./ngrok.exe http 8001"
        echo ""
        echo "📊 Ver logs: docker-compose logs -f"
        echo "⏹️  Parar: docker-compose down"
        exit 0
    fi
    printf "."
    sleep 2
done

echo ""
echo "⚠️  El servicio tardó más de lo esperado"
echo "📋 Ver logs: docker-compose logs -f web"
echo "🔄 Reintentar: docker-compose restart"