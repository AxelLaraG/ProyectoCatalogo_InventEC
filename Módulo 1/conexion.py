from pymongo import MongoClient

def conectar_mongo():
    try:
        cliente = MongoClient("mongodb+srv://axmadlar:pw1234@cluster0.rrnubrd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        db = cliente["proyecto"]  # Base de datos: "proyecto"
        return db
    except Exception as e:
        print("Error al conectar a MongoDB:", e)
        return None
