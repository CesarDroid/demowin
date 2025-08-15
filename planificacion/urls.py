# planificacion/urls.py
from django.urls import path
from . import views

app_name = 'planificacion'

urlpatterns = [
    # Autenticación
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard principal
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Gestión de Mufas
    path('mufas/', views.mufas_list, name='mufas_list'),
    path('mufas/crear/', views.mufa_create, name='mufa_create'),
    path('mufas/<int:pk>/', views.mufa_detail, name='mufa_detail'),
    path('mufas/<int:pk>/editar/', views.mufa_edit, name='mufa_edit'),
    path('mufas/<int:pk>/eliminar/', views.mufa_delete, name='mufa_delete'),
    
    # Gestión de Cables Troncales
    path('cables-troncales/', views.cables_troncales_list, name='cables_troncales_list'),
    path('cables-troncales/crear/', views.cable_troncal_create, name='cable_troncal_create'),
    path('cables-troncales/<int:pk>/', views.cable_troncal_detail, name='cable_troncal_detail'),
    path('cables-troncales/<int:pk>/editar/', views.cable_troncal_edit, name='cable_troncal_edit'),
    
    # Gestión de Cables de Derivación
    path('derivaciones/', views.derivaciones_list, name='derivaciones_list'),
    path('derivaciones/crear/', views.derivacion_create, name='derivacion_create'),
    path('derivaciones/<int:pk>/', views.derivacion_detail, name='derivacion_detail'),
    path('derivaciones/<int:pk>/editar/', views.derivacion_edit, name='derivacion_edit'),
    path('derivaciones/<int:pk>/eliminar/', views.derivacion_delete, name='derivacion_delete'),
    
    # Gestión de Slots
    path('slots/', views.slots_list, name='slots_list'),
    path('slots/crear/', views.slot_create, name='slot_create'),
    path('slots/<int:pk>/editar/', views.slot_edit, name='slot_edit'),
    
    # APIs para datatables y componentes
    path('api/mufas/', views.api_mufas, name='api_mufas'),
    path('api/derivaciones/', views.api_derivaciones, name='api_derivaciones'),
    path('api/estadisticas/', views.api_estadisticas, name='api_estadisticas'),
]