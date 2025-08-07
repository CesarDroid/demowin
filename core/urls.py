# core/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('mufas/', include('mufas.urls', namespace='mufas')),
    path('proyectos/', include('proyectos.urls', namespace='proyectos')),
    path('roles/', include('roles.urls', namespace='roles')),
]
