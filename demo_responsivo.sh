#!/bin/bash

echo "🚀 WinFibra - Demo Responsivo FINAL"
echo "=================================="

# Detectar Python
if [ -f "C:/Users/elray/AppData/Local/Programs/Python/Python312/python.exe" ]; then
    PYTHON_CMD="C:/Users/elray/AppData/Local/Programs/Python/Python312/python.exe"
else
    PYTHON_CMD="python"
fi

# Terminar procesos previos
taskkill //F //IM python.exe 2>/dev/null || true
sleep 1

echo ""
echo "🎉 DEMO MÓVIL RESPONSIVO LISTO"
echo "============================="
echo ""
echo "📱 URL PRINCIPAL:"
echo "   http://localhost:8000"
echo ""
echo "📱 CÓMO PROBAR RESPONSIVIDAD:"
echo "   1. Abrir http://localhost:8000 en navegador"
echo "   2. Presionar F12 (Developer Tools)"
echo "   3. Activar Device Toolbar (icono móvil)"
echo "   4. Probar: iPhone SE, iPhone 12 Pro, iPad"
echo "   5. Cambiar orientación vertical/horizontal"
echo ""
echo "🌐 PARA DEMO REMOTO:"
echo "   En otra terminal: ./ngrok.exe http 8000"
echo ""
echo "✨ CARACTERÍSTICAS IMPLEMENTADAS:"
echo "   • Navegación hamburger responsive"
echo "   • Tarjetas métricas adaptables"
echo "   • Botones táctiles optimizados"
echo "   • Breakpoints: 768px, 480px"
echo "   • Touch-friendly interactions"
echo ""
echo "🚀 Servidor HTTP simple iniciando..."

# Servidor HTTP simple en puerto 8000
"$PYTHON_CMD" -m http.server 8000 --bind 0.0.0.0