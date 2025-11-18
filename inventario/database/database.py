from pymongo import MongoClient

client = MongoClient("mongodb://mongodb:27017/")
db = client["inventario"]

async def get_db():
    indices = db.productos.index_information()
    if "codigo_barras" not in indices:
        db.productos.create_index("codigo_barras", unique=True)
    yield db