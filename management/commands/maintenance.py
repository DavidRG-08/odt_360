
from django.core.management.base import BaseCommand
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Activa o desactiva el modo de mantenimiento'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            type=str,
            choices=['on', 'off', 'status'],
            help='on: Activar mantenimiento, off: Desactivar, status: Ver estado'
        )

    def handle(self, *args, **options):
        action = options['action']
        maintenance_file = os.path.join(settings.BASE_DIR, '.maintenance')

        if action == 'on':
            # Crear archivo de mantenimiento
            open(maintenance_file, 'a').close()
            self.stdout.write(
                self.style.SUCCESS('✓ Modo de mantenimiento ACTIVADO')
            )
            self.stdout.write(
                'Los usuarios verán la página de mantenimiento.'
            )

        elif action == 'off':
            # Eliminar archivo de mantenimiento
            if os.path.exists(maintenance_file):
                os.remove(maintenance_file)
                self.stdout.write(
                    self.style.SUCCESS('✓ Modo de mantenimiento DESACTIVADO')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('El modo de mantenimiento no está activado')
                )

        elif action == 'status':
            if os.path.exists(maintenance_file):
                self.stdout.write(
                    self.style.SUCCESS('✓ Modo de mantenimiento: ACTIVO')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('✗ Modo de mantenimiento: INACTIVO')
                )

