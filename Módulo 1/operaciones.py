def obtener_todos_los_equipos(coleccion):
    return list(coleccion.find())

def buscar_equipos(coleccion, query):
    if not query:
        return obtener_todos_los_equipos(coleccion)
    
    filtros = {
        "$or": [
            {"nombre": {"$regex": query, "$options": "i"}},
            {"modelo": {"$regex": query, "$options": "i"}},
            {"estado": {"$regex": query, "$options": "i"}}
        ]
    }
    return list(coleccion.find(filtros))

def filtrar_por_estado(coleccion, estado):
    if estado.lower() == "todos":
        return obtener_todos_los_equipos(coleccion)
    return list(coleccion.find({"estado": {"$regex": f"^{estado}$", "$options": "i"}}))

def buscar_por_campo(coleccion, campo, valor):
    if campo == "todos":
        return list(coleccion.find())

    if campo == "estado":
        filtro = {campo: {"$regex": f"^{valor}$", "$options": "i"}}
    else:
        filtro = {campo: {"$regex": valor, "$options": "i"}}

    return list(coleccion.find(filtro))

def buscar_con_filtro_combinado(coleccion, campo, valor, estado):
    filtros = {}

    # Búsqueda por campo
    if campo != "todos" and valor:
        if campo == "estado":
            filtros[campo] = {"$regex": f"^{valor}$", "$options": "i"}
        else:
            filtros[campo] = {"$regex": valor, "$options": "i"}

    # Filtro por estado
    if estado != "todos":
        filtros["estado"] = {"$regex": f"^{estado}$", "$options": "i"}

    return list(coleccion.find(filtros))

