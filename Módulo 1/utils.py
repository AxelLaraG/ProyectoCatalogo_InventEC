def capitalizar(texto):
    return texto.capitalize() if isinstance(texto, str) else texto

def formatear_valor(valor):
    return valor if valor is not None else ""
