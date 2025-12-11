# radicacion_app/tests.py
from django.test import TestCase, TransactionTestCase
from django.db import transaction
from concurrent.futures import ThreadPoolExecutor
from .models import ParametrosRadicacion, RadicacionRecibidos, TipoComunicacion

class ConsecutivoSeguroTest(TransactionTestCase):
    """Test para verificar que los consecutivos sean únicos incluso con usuarios simultáneos"""
    
    def setUp(self):
        tipo = TipoComunicacion.objects.create(tipo="Comunicaciones recibidas")

        self.parametro = ParametrosRadicacion.objects.create(
            prefijo='ODT',
            year=2025,
            tipo_comunicacion= tipo,
            consecutivo=100
        )
    
    def test_consecutivos_unicos_concurrentes(self):
        """Verifica que con 10 threads simultáneos todos obtengan IDs únicos"""
        ids_generados = []
        
        def generar_id():
            id_generado = self.parametro.generar_id_radicado()
            ids_generados.append(id_generado)
        
        # Ejecutar 10 threads simultáneamente
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(generar_id) for _ in range(10)]
            for future in futures:
                future.result()
        
        # Verificar que todos sean únicos
        self.assertEqual(len(ids_generados), len(set(ids_generados)))
        print(f"✓ IDs generados: {ids_generados}")