from fastapi import FastAPI
from logic.logic_producto import router as producto
from logic.logic_item import router as item
from logic.logic_bodega import router as bodega
app = FastAPI()
app.include_router(producto)
app.include_router(item)
app.include_router(bodega)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Inventory Management System"}
