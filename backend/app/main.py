from fastapi import FastAPI, HTTPException
from app.routes.calls import router as calls_router
from app.database import check_supabase_connection

app = FastAPI(
    title = "Cold Call Copilot",
    description = "Backend API for the Cold Call Collection",
    version = "0.1.0",
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
