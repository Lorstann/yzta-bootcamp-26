from fastapi import FastAPI
from backend.api.routes import health

app = FastAPI(
    title="Equa API",
    version="1.0.0",
    description="Equa B2B2C MVP API"
)

# Router'ı dahil ediyoruz
app.include_router(health.router, prefix="/api/v1")