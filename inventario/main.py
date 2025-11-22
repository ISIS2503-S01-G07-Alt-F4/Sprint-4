from fastapi import FastAPI
from logic.logic_producto import router as producto
from logic.logic_item import router as item
from logic.logic_bodega import router as bodega
from logic.logic_estanteria import router as estanteria
app = FastAPI()
app.include_router(producto)
app.include_router(item)
app.include_router(bodega)
app.include_router(estanteria)
@app.get("/")
async def read_root():
    return {"message": "Bienvenido al Microservicio de Inventario :)"}
