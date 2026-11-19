from supabase import Client, create_client
from .config import settings

client: Client | None = None


def connect_to_supabase() -> None:
    """Create the Supabase client and verify that the database is reachable."""
    global client
    if not settings.supabase_url or not settings.supabase_key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in backend/.env")
    client = create_client(settings.supabase_url, settings.supabase_key)
    # A lightweight query verifies credentials and that the expected table exists.
    client.table("conversations").select("id").limit(1).execute()


def close_supabase_connection() -> None:
    global client
    client = None


def get_database() -> Client:
    if client is None:
        raise RuntimeError("Supabase is not connected")
    return client
