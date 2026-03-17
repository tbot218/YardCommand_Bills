# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.db.database import Base, engine
from backend.api import auth, bills, crew, clients, jobs


# =============================================================
# INITIALISE DATABASE
# =============================================================
Base.metadata.create_all(bind=engine)


# =============================================================
# CREATE FASTAPI APP
# =============================================================
app = FastAPI(
    title="Yard Command Backend",
    description="Backend API for Yard Command (Crew + Admin System)",
    version="1.0.0"
)


# =============================================================
# CORS SETTINGS (Allow UI + Cloudflare Tunnel)
# =============================================================
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:5500",
    "https://*.trycloudflare.com",  # for Cloudflare Tunnel access
    "*"  # TEMPORARY during development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================
# ROOT ENDPOINT
# =============================================================
@app.get("/")
def root():
    return {"status": "ok", "message": "Yard Command backend running"}


# =============================================================
# API ROUTERS
# =============================================================
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(crew.router, prefix="/crew", tags=["Crew"])
app.include_router(clients.router, prefix="/clients", tags=["Clients"])
app.include_router(bills.router, prefix="/bills", tags=["Bills"])
app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
import logging
logging.basicConfig(level=logging.DEBUG)
