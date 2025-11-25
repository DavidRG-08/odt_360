
from django.shortcuts import render
from django.conf import settings
import os

class MaintenanceMiddleware:
    """
    Middleware que muestra una página de mantenimiento si existe
    un archivo de control en el proyecto.
    
    Para activar mantenimiento:
        - Crea un archivo vacío: .maintenance
        - En la raíz del proyecto
    
    Para desactivar mantenimiento:
        - Elimina el archivo: .maintenance
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.maintenance_file = os.path.join(settings.BASE_DIR, '.maintenance')
    
    def __call__(self, request):
        # Verificar si existe el archivo de mantenimiento
        if os.path.exists(self.maintenance_file):
            # Permitir acceso a admin durante mantenimiento
            if request.path.startswith('/admin/'):
                return self.get_response(request)
            
            # Mostrar página de mantenimiento
            return render(request, 'maintenance.html', status=503)
        
        response = self.get_response(request)
        return response

