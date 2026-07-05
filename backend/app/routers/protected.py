from fastapi import APIRouter, Depends, Header, HTTPException

from app.services.session import decode_session_token
from app.services.supabase_client import supabase

router = APIRouter()


async def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    """Dependency: extracts and validates the Bearer session token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split(" ", 1)[1]
    payload = decode_session_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired session token")

    return payload


@router.get("/profile/me")
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    """Example protected endpoint: only reachable with a valid session token."""
    result = (
        supabase.table("producers")
        .select("*")
        .eq("id", current_user["sub"])
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Profile not found")

    return result.data[0]
