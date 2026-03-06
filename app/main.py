from fastapi import FastAPI
from app.api.routes import router as core_router
from app.api.audit import router as audit_router
from app.api import audit_integrity
from app.api import cases
from app.api import accounts
from app.api import profile
from app.api import metrics
from app.api import transactions
from app.api import system
from fastapi.middleware.cors import CORSMiddleware
from app.core.startup import initialize_database
from app.core.logging import get_logger


app = FastAPI(
    title="Aegis Risk Intelligence Platform",
    version="0.1",
)

# Register all routes from one place
app.include_router(core_router)
app.include_router(audit_router)
app.include_router(cases.router)
app.include_router(accounts.router)
app.include_router(profile.router)
app.include_router(metrics.router)
app.include_router(transactions.router)
app.include_router(system.router)
app.include_router(audit_integrity.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/health")
def health():
    return {"status": "ok"}

@app.on_event("startup")
def startup_event():
    logger = get_logger("aegis.startup")
    initialize_database()
    logger.info("Aegis backend startup completed successfully.")
