from fastapi import FastAPI
from logic.logic_audit_logs import router as audit_log_router
from logic.logic_audited_service import router as audited_service_router

app = FastAPI()
app.include_router(audit_log_router)
app.include_router(audited_service_router)

@app.get("/")
async def root():
    return {"message": "Bienvenido al servicio de auditoría de Provesi"}