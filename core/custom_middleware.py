# core/custom_middleware.py - Middleware para ocultar Django
class HideDjangoMiddleware:
    """
    Middleware para ocultar que el sistema está hecho con Django
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Remover headers que revelan Django
        if 'Server' in response:
            response['Server'] = 'WinFibra/1.0'
        
        # Cambiar X-Frame-Options header
        response['X-Powered-By'] = 'WinFibra System'
        
        # Agregar headers personalizados
        response['X-System'] = 'WinFibra Infrastructure Management'
        
        # Remover el header Content-Type específico de Django en algunas respuestas
        if hasattr(response, 'get') and 'django' in str(response.get('Content-Type', '')).lower():
            response['Content-Type'] = response.get('Content-Type', '').replace('Django', 'WinFibra')
        
        return response


class CustomErrorMiddleware:
    """
    Middleware para personalizar páginas de error sin mencionar Django
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """
        Procesar excepciones para mostrar errores personalizados
        """
        # En lugar de mostrar errores de Django, mostrar errores genéricos
        return None  # Dejar que Django maneje normalmente, pero con templates personalizados