# mufas/urls.py - VERSIÓN ACTUALIZADA

from django.urls import path
from . import views

app_name = 'mufas'

urlpatterns = [
    # Mapa principal con controles avanzados
    path('mapa/',            views.mapa_mufas,      name='mapa_mufas'),
    
    # APIs JSON para el mapa
    path('mufas_json/',      views.obtener_mufas,   name='mufas_json'),
    path('cables_json/',     views.obtener_cables,  name='cables_json'),
    path('conexiones_json/', views.obtener_conexiones, name='conexiones_json'),
    
    # Nueva API para estadísticas generales del panel de control
    path('estadisticas/',    views.obtener_estadisticas_generales, name='estadisticas'),
    
    # AJAX para asignar hilo
    path('asignar_hilo/',    views.asignar_hilo,    name='asignar_hilo'),
]