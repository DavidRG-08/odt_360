import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
maintenance_file = os.path.join(BASE_DIR, '.maintenance')

if len(sys.argv) > 1:
    action = sys.argv[1]
    
    if action == 'on':
        open(maintenance_file, 'a').close()
        print('✓ Modo de mantenimiento ACTIVADO')
    elif action == 'off':
        if os.path.exists(maintenance_file):
            os.remove(maintenance_file)
            print('✓ Modo de mantenimiento DESACTIVADO')
        else:
            print('⚠ El modo de mantenimiento no está activado')
    elif action == 'status':
        if os.path.exists(maintenance_file):
            print('✓ Modo de mantenimiento: ACTIVO')
        else:
            print('✗ Modo de mantenimiento: INACTIVO')
else:
    print('Uso: python maintenance.py [on|off|status]')