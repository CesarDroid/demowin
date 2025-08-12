# roles/management/commands/init_roles.py - Inicializar Roles y Áreas
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from roles.models import AreaTrabajo, RolUsuario, PerfilUsuario

class Command(BaseCommand):
    help = 'Inicializar áreas de trabajo y roles del sistema WinFibra'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Inicializando sistema de roles WinFibra...')
        )

        # 1. Crear Áreas de Trabajo
        areas_data = [
            {
                'codigo': 'comercial',
                'nombre': 'Área Comercial',
                'descripcion': 'Encargada de la captación de clientes y creación de proyectos comerciales'
            },
            {
                'codigo': 'planificacion',
                'nombre': 'Área de Planificación',
                'descripcion': 'Responsable del registro de hilos y asignación a edificios'
            },
            {
                'codigo': 'construccion',
                'nombre': 'Área de Construcción',
                'descripcion': 'Ejecuta los proyectos y realiza la instalación física'
            },
            {
                'codigo': 'administracion',
                'nombre': 'Administración',
                'descripcion': 'Gestión general del sistema y supervisión'
            }
        ]

        self.stdout.write('📋 Creando áreas de trabajo...')
        for area_info in areas_data:
            area, created = AreaTrabajo.objects.get_or_create(
                codigo=area_info['codigo'],
                defaults={
                    'nombre': area_info['nombre'],
                    'descripcion': area_info['descripcion'],
                    'activa': True
                }
            )
            if created:
                self.stdout.write(f'   ✅ Área creada: {area.nombre}')
            else:
                self.stdout.write(f'   ℹ️  Área existe: {area.nombre}')

        # 2. Crear Roles
        roles_data = [
            # Área Comercial
            {
                'codigo': 'comercial',
                'nombre': 'Comercial',
                'area_codigo': 'comercial',
                'descripcion': 'Crea proyectos comerciales y gestiona clientes',
                'permisos': {
                    'puede_crear_proyectos': True,
                    'puede_editar_proyectos': True,
                    'puede_ver_dashboard': True,
                    'puede_ver_analytics': True,
                }
            },
            {
                'codigo': 'supervisor_comercial',
                'nombre': 'Supervisor Comercial',
                'area_codigo': 'comercial',
                'descripcion': 'Supervisa el área comercial y todos los proyectos',
                'permisos': {
                    'puede_crear_proyectos': True,
                    'puede_editar_proyectos': True,
                    'puede_ver_dashboard': True,
                    'puede_ver_analytics': True,
                    'puede_ver_mapa_mufas': True,
                }
            },
            
            # Área de Planificación
            {
                'codigo': 'planificador',
                'nombre': 'Planificador',
                'area_codigo': 'planificacion',
                'descripcion': 'Registra hilos y los asigna a edificios',
                'permisos': {
                    'puede_asignar_hilos': True,
                    'puede_ver_mapa_mufas': True,
                    'puede_ver_dashboard': True,
                }
            },
            {
                'codigo': 'supervisor_planificacion',
                'nombre': 'Supervisor de Planificación',
                'area_codigo': 'planificacion',
                'descripcion': 'Supervisa la planificación y asignación de recursos',
                'permisos': {
                    'puede_asignar_hilos': True,
                    'puede_ver_mapa_mufas': True,
                    'puede_ver_dashboard': True,
                    'puede_ver_analytics': True,
                    'puede_editar_proyectos': True,
                }
            },
            
            # Área de Construcción
            {
                'codigo': 'constructor',
                'nombre': 'Constructor',
                'area_codigo': 'construccion',
                'descripcion': 'Ejecuta proyectos y visualiza hilos asignados',
                'permisos': {
                    'puede_ver_mapa_mufas': True,
                    'puede_ver_dashboard': True,
                }
            },
            {
                'codigo': 'supervisor_construccion',
                'nombre': 'Supervisor de Construcción',
                'area_codigo': 'construccion',
                'descripcion': 'Supervisa la construcción y ejecución de proyectos',
                'permisos': {
                    'puede_ver_mapa_mufas': True,
                    'puede_ver_dashboard': True,
                    'puede_ver_analytics': True,
                    'puede_editar_proyectos': True,
                }
            },
            
            # Administración
            {
                'codigo': 'admin_sistema',
                'nombre': 'Administrador del Sistema',
                'area_codigo': 'administracion',
                'descripcion': 'Acceso completo al sistema',
                'permisos': {
                    'puede_crear_proyectos': True,
                    'puede_editar_proyectos': True,
                    'puede_asignar_hilos': True,
                    'puede_ver_dashboard': True,
                    'puede_ver_mapa_mufas': True,
                    'puede_ver_analytics': True,
                }
            }
        ]

        self.stdout.write('👥 Creando roles de usuario...')
        for rol_info in roles_data:
            area = AreaTrabajo.objects.get(codigo=rol_info['area_codigo'])
            rol, created = RolUsuario.objects.get_or_create(
                codigo=rol_info['codigo'],
                defaults={
                    'nombre': rol_info['nombre'],
                    'area': area,
                    'descripcion': rol_info['descripcion']
                }
            )
            if created:
                self.stdout.write(f'   ✅ Rol creado: {rol.nombre} ({area.nombre})')
            else:
                self.stdout.write(f'   ℹ️  Rol existe: {rol.nombre} ({area.nombre})')

        # 3. Asignar rol de administrador al usuario admin si existe
        try:
            admin_user = User.objects.get(username='admin')
            admin_rol = RolUsuario.objects.get(codigo='admin_sistema')
            
            perfil, created = PerfilUsuario.objects.get_or_create(
                usuario=admin_user,
                defaults={
                    'rol': admin_rol,
                    'activo': True,
                    'puede_crear_proyectos': True,
                    'puede_editar_proyectos': True,
                    'puede_asignar_hilos': True,
                    'puede_ver_dashboard': True,
                    'puede_ver_mapa_mufas': True,
                    'puede_ver_analytics': True,
                }
            )
            
            if created:
                self.stdout.write(f'   ✅ Perfil admin creado: {perfil}')
            else:
                # Actualizar permisos si ya existe
                perfil.rol = admin_rol
                perfil.puede_crear_proyectos = True
                perfil.puede_editar_proyectos = True
                perfil.puede_asignar_hilos = True
                perfil.puede_ver_dashboard = True
                perfil.puede_ver_mapa_mufas = True
                perfil.puede_ver_analytics = True
                perfil.save()
                self.stdout.write(f'   🔄 Perfil admin actualizado: {perfil}')
                
        except User.DoesNotExist:
            self.stdout.write('   ⚠️  Usuario admin no encontrado')

        # 4. Mostrar resumen
        self.stdout.write('\n📊 RESUMEN:')
        self.stdout.write(f'   📋 Áreas creadas: {AreaTrabajo.objects.count()}')
        self.stdout.write(f'   👥 Roles creados: {RolUsuario.objects.count()}')
        self.stdout.write(f'   👤 Perfiles de usuario: {PerfilUsuario.objects.count()}')

        # 5. Mostrar roles por área
        self.stdout.write('\n🏢 ROLES POR ÁREA:')
        for area in AreaTrabajo.objects.all():
            self.stdout.write(f'   {area.nombre}:')
            for rol in area.roles.all():
                usuarios_count = rol.usuarios.count()
                self.stdout.write(f'      • {rol.nombre} ({usuarios_count} usuarios)')

        self.stdout.write('\n🎉 ¡Sistema de roles inicializado correctamente!')
        self.stdout.write('💡 Usa el admin de Django para gestionar usuarios y asignar roles.')
        
        # Instrucciones
        self.stdout.write('\n📝 PRÓXIMOS PASOS:')
        self.stdout.write('   1. Crear usuarios desde el admin: /admin/auth/user/')
        self.stdout.write('   2. Asignar roles en la sección "Perfil del Usuario"')
        self.stdout.write('   3. Las interfaces se adaptarán automáticamente según el rol')