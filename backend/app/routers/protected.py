from fastapi import APIRouter, Depends, Header, HTTPException

from app.services.session import decode_session_token
from app.services import supabase_client
from app.services.frames import get_equipped_frame

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
    result = await supabase_client.supabase.table("producers").select("*").eq("id", current_user["sub"]).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Profile not found")

    producer = result.data[0]
    frame = await get_equipped_frame(current_user["sub"])

    return {
        "name": producer["first_name"],
        "tier": producer["tier"],
        "level": producer["level"],
        "avatarUrl": producer.get("equipped_avatar_url") or producer.get("photo_url"),
        "verified": producer["verified"],
        "voteTickets": producer["vote_tickets"],
        "xp": {"current": producer["xp_current"], "max": producer["xp_max"]},
        "votesCast": producer["votes_cast"],
        "diamonds": producer["diamonds"],
        "achievementsUnlocked": len(producer.get("recent_badges") or []),
        "recentBadges": producer.get("recent_badges") or [],
        "equippedFrame": frame,
    }
