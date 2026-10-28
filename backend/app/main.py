import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routes.calls import router as calls_router
from app.database import check_supabase_connection

app = FastAPI(
    title = "Cold Call Copilot",
    description = "Backend API for the Cold Call Collection",
    version = "0.1.0",
)

allowed_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
configured_origins = os.getenv("FRONTEND_ORIGIN", "")
allowed_origins.extend(
    origin.strip()
    for origin in configured_origins.split(",")
    if origin.strip()
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(calls_router)

@app.get("/health")
def health_check() -> dict[str,str]:
    """Report whether the API process is responding."""
    return {"status":"ok"}


@app.get("/health/supabase")
def supabase_health_check() -> dict[str, str]:
    """Check backend credentials and access to the calls table."""
    try:
        check_supabase_connection()
    except Exception as exc:
        # Keep credentials and provider details out of the response.
        raise HTTPException(
            status_code=503,
            detail="Supabase connection failed. Check backend configuration and table access.",
        ) from exc

    return {"status": "ok", "supabase": "connected"}
