from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Aegis Risk Intelligence Platform",
    version="0.1"
)

# Register routes
app.include_router(router)
