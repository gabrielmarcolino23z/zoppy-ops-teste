from fastapi import FastAPI
from src.api.routes.linkedin_post_controller import router as linkedin_post_router
from src.api.routes.plan_action_90d_controller import router as plan_action_90d_router
from src.api.routes.copy_wpp_controller import router as copy_wpp_router
from src.api.routes.copy_sms_controller import router as copy_sms_router
from src.config.settings import get_settings

settings = get_settings()

app = FastAPI()

app.include_router(linkedin_post_router, prefix="/api")
app.include_router(plan_action_90d_router, prefix="/api")
app.include_router(copy_wpp_router, prefix="/api")
app.include_router(copy_sms_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "API ON"}

@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde da API"""
    return {"status": "ok"}