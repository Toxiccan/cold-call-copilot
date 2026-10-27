"""Supabase client configuration for the FastAPI backend."""

import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import Client, create_client


# Load backend/.env when running locally. In production, the hosting service
# should provide these values as environment variables instead.
BACKEND_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(BACKEND_ENV_FILE)


def get_supabase_client() -> Client:
    """Create a Supabase client without exposing its secret key."""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")

    if not supabase_url or not supabase_service_key:
        raise RuntimeError("Supabase environment variables are not configured.")

    return create_client(supabase_url, supabase_service_key)


def check_supabase_connection() -> bool:
    """Check that the API can read from the calls table."""
    client = get_supabase_client()
    client.table("calls").select("id").limit(1).execute()
    return True
