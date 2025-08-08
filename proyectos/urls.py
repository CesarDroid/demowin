from django.urls import path
from django.shortcuts import render

app_name = "proyectos"

def proyecto_dashboard(request):
    return render(request, 'proyectos/dashboard.html', {'demo': True})

def proyecto_list(request):
    return render(request, 'proyectos/proyecto_list.html', {'proyectos': []})

urlpatterns = [
    path("", proyecto_dashboard, name="dashboard"),
    path("lista/", proyecto_list, name="list"),
]