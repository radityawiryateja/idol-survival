from fastapi import APIRouter, Depends, HTTPException

from app.routers.protected import get_current_user
from app.services.missions import get_or_create_today_missions
from app.services.supabase_client import supabase

router = APIRouter()


@router.get("/dashboard/summary")
async def dashboard_summary(current_user: dict = Depends(get_current_user)):
    producer_result = supabase.table("producers").select("*").eq("id", current_user["sub"]).execute()
    if not producer_result.data:
        raise HTTPException(status_code=404, detail="Producer not found")
    producer = producer_result.data[0]

    config = supabase.table("app_config").select("*").eq("id", 1).execute().data
    config = config[0] if config else {}

    top_idols = supabase.table("idols").select("*").order("votes", desc=True).limit(3).execute().data
    featured_idols = [
        {"id": idol["id"], "name": idol["name"], "photo": idol["photo_url"], "rank": index}
        for index, idol in enumerate(top_idols, start=1)
    ]

    missions = await get_or_create_today_missions(producer["id"])

    return {
        "profile": {
            "name": producer["first_name"],
            "tier": producer["tier"],
            "level": producer["level"],
            "avatarUrl": producer["photo_url"],
        },
        "season": {"daysLeft": config.get("days_left", 0)},
        "stats": {
            "voteTickets": producer["vote_tickets"],
            "diamonds": producer["diamonds"],
            "supporterPoints": producer["supporter_points"],
            "supporterCap": producer["supporter_cap"],
        },
        "liveBanner": {
            "title": config.get("live_banner_title", ""),
            "viewers": config.get("live_banner_viewers", ""),
            "image": config.get("live_banner_image", ""),
        },
        "featuredIdols": featured_idols,
        "missions": missions,
    }
