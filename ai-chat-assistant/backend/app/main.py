import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import connect_to_supabase, close_supabase_connection
from .routes.chat import router

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        connect_to_supabase()
        logging.info("Connected to Supabase")
    except Exception:
        logging.exception("Could not connect to Supabase")
        raise
    yield
    close_supabase_connection()

app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
app.include_router(router)

@app.get("/api/health")
async def health():
    from .database import get_database
    try:
        get_database().table("conversations").select("id").limit(1).execute()
        return {"status": "ok", "database": "connected", "provider": "supabase"}
    except Exception:
        return {"status": "degraded", "database": "unavailable"}
