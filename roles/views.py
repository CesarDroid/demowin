# roles/views.py
from django.views import View
from django.http import HttpResponse

class InitRolesView(View):
    def get(self, request):
        # aquí llamas a tu comando de inicialización o lógica
        from .management.commands.init_roles import Command
        cmd = Command()
        cmd.handle()
        return HttpResponse("Roles inicializados")
