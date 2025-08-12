# roles/management/commands/init_roles.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mufas.models import Mufa, Hilo, Conexion

class Command(BaseCommand):
    help = "Inicializa roles y permisos para Planificador, Coordinador, Supervisor, JefeÁrea y GerenteÁrea"

    def handle(self, *args, **options):
        # ContentTypes de los modelos de mufas
        ct_mufa  = ContentType.objects.get_for_model(Mufa)
        ct_hilo  = ContentType.objects.get_for_model(Hilo)
        ct_conx  = ContentType.objects.get_for_model(Conexion)

        # Permisos a usar
        perms = {
            'view_mufa':       Permission.objects.get(codename='view_mufa',       content_type=ct_mufa),
            'add_mufa':        Permission.objects.get(codename='add_mufa',        content_type=ct_mufa),
            'change_mufa':     Permission.objects.get(codename='change_mufa',     content_type=ct_mufa),

            'view_hilo':       Permission.objects.get(codename='view_hilo',       content_type=ct_hilo),
            'change_hilo':     Permission.objects.get(codename='change_hilo',     content_type=ct_hilo),

            'view_conexion':   Permission.objects.get(codename='view_conexion',   content_type=ct_conx),
            'add_conexion':    Permission.objects.get(codename='add_conexion',    content_type=ct_conx),
            'change_conexion': Permission.objects.get(codename='change_conexion', content_type=ct_conx),
        }

        # 1) Planificador: puede ver y cambiar Hilo
        plan = Group.objects.get_or_create(name='Planificador')[0]
        plan.permissions.set([perms['view_hilo'], perms['change_hilo']])

        # 2) Coordinador: ve mufa/hilo y puede añadir/cambiar Conexión
        coord = Group.objects.get_or_create(name='Coordinador')[0]
        coord.permissions.set([
            perms['view_mufa'], perms['view_hilo'],
            perms['add_conexion'], perms['change_conexion'], perms['view_conexion'],
        ])

        # 3) Supervisor: solo ve mufa, hilo y conexión
        sup = Group.objects.get_or_create(name='Supervisor')[0]
        sup.permissions.set([
            perms['view_mufa'], perms['view_hilo'], perms['view_conexion']
        ])

        # 4) Jefe de Área: gestiona mufas además de ver todo
        jefe = Group.objects.get_or_create(name='JefeÁrea')[0]
        jefe.permissions.set([
            perms['view_mufa'], perms['add_mufa'], perms['change_mufa'],
            perms['view_hilo'], perms['view_conexion']
        ])

        # 5) Gerente de Área: todos los permisos de la app mufas
        gerente = Group.objects.get_or_create(name='GerenteÁrea')[0]
        # Filtramos solo los permisos de la app 'mufas'
        gerente.permissions.set(Permission.objects.filter(content_type__app_label='mufas'))

        self.stdout.write(self.style.SUCCESS("✅ Roles y permisos inicializados exitosamente"))
