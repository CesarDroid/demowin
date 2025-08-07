# roles/urls.py
from django.urls import path
from . import views

app_name = "roles"

urlpatterns = [
    # ejemplo de vista para inicializar roles
    path("init/", views.InitRolesView.as_view(), name="init_roles"),
]
