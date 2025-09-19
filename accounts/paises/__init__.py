# accounts/paises/__init__.py

def get_ciudades_por_pais(pais):
    if pais == "ecuador":
        from .ecuador import CIUDADES_PRINCIPALES
        return CIUDADES_PRINCIPALES
    # Aquí puedes agregar más países en el futuro
    return []
