import holidays
from datetime import datetime, timedelta

def calcular_fecha_maxima_respuesta(dias_habiles):
    """
    Calcula la fecha máxima de respuesta sumando días hábiles.
    Excluye sábados, domingos y festivos de Colombia.
    
    Args:
        dias_habiles (int): Número de días hábiles a sumar
    
    Returns:
        datetime: Fecha calculada
    """
    # Obtener festivos de Colombia del año actual
    festivos_colombia = holidays.Colombia(years=datetime.now().year)
    
    fecha_actual = datetime.now().date()
    dias_sumados = 0
    fecha_resultado = fecha_actual
    
    while dias_sumados < dias_habiles:
        fecha_resultado += timedelta(days=1)
        
        # Verificar si es fin de semana (5=sábado, 6=domingo)
        if fecha_resultado.weekday() < 5:
            # Verificar si NO es festivo
            if fecha_resultado not in festivos_colombia:
                dias_sumados += 1
    
    return fecha_resultado


def obtener_festivos_colombia():
    """
    Retorna una lista de festivos de Colombia para el año actual.
    Útil para validaciones en frontend.
    
    Returns:
        list: Lista de fechas en formato 'YYYY-MM-DD'
    """
    festivos = holidays.Colombia(years=datetime.now().year)
    return [fecha.strftime('%Y-%m-%d') for fecha in festivos.keys()]