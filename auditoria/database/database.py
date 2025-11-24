from pymongo import MongoClient

client = MongoClient("mongodb://mongodb_audit:27017/")
db = client["audit"]

async def get_db():
    yield db
    
def get_next_id(sequence_name: str) -> str:
    """
    Incrementa y devuelve el siguiente ID para una secuencia específica.
    """
    contador = db.contador.find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"valor_secuencia": 1}},
        upsert=True,
        return_document=True
    )
    return str(contador["valor_secuencia"])