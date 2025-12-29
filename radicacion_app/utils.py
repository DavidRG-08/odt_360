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


def calcular_fecha_vencimiento_ley(fecha_inicio, dias=15):
    """
    Calcula la fecha de vencimiento por ley sumando días hábiles
    (excluyendo fines de semana y festivos).
    
    Args:
        fecha_inicio: fecha de inicio (datetime.date o string 'YYYY-MM-DD')
        dias: número de días hábiles a sumar (default: 15)
    
    Returns:
        datetime.date con la fecha de vencimiento
    """
    from datetime import datetime, timedelta
    
    # Convertir string a date si es necesario
    if isinstance(fecha_inicio, str):
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    
    festivos = obtener_festivos_colombia()
    festivos_dates = [datetime.strptime(f, '%Y-%m-%d').date() for f in festivos]
    
    fecha_actual = fecha_inicio
    dias_contados = 0
    
    while dias_contados < dias:
        fecha_actual += timedelta(days=1)
        
        # Verificar que no sea fin de semana (5=sábado, 6=domingo)
        if fecha_actual.weekday() < 5:
            # Verificar que no sea festivo
            if fecha_actual not in festivos_dates:
                dias_contados += 1
    
    return fecha_actual



def calcular_fecha_vencimiento_interno(fecha_inicio, dias=7):
    """
    Calcula la fecha de vencimiento interno sumando días corridos
    (sin excluir fines de semana ni festivos).
    
    Args:
        fecha_inicio: fecha de inicio (datetime.date o string 'YYYY-MM-DD')
        dias: número de días corridos a sumar (default: 7)
    
    Returns:
        datetime.date con la fecha de vencimiento
    """
    from datetime import datetime, timedelta
    
    # Convertir string a date si es necesario
    if isinstance(fecha_inicio, str):
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    
    return fecha_inicio + timedelta(days=dias)