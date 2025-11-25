def obtener_modulos_visibles(modulos_config, user):
    """
    Función centralizada para obtener módulos según grupos del usuario.
    Úsala en cualquier app del proyecto.
    
    Args:
        modulos_config (list): Lista de diccionarios con configuración de módulos
        user (User): Usuario a validar
    
    Returns:
        list: Lista de módulos visibles para el usuario
    """
    user_groups = set(user.groups.values_list('name', flat=True))
    modulos_visibles = []
    
    for modulo in modulos_config:
        if 'todos' in modulo.get('grupos', []):
            modulos_visibles.append(modulo)
        elif any(grupo in user_groups for grupo in modulo.get('grupos', [])):
            modulos_visibles.append(modulo)
    
    return modulos_visibles