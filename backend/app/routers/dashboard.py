import asyncio

from fastapi import APIRouter, Depends, HTTPException

from app.routers.protected import get_current_user
from app.services.missions import get_or_create_today_missions
from app.services import supabase_client
from app.services.frames import get_equipped_frame

router = APIRouter()


@router.get("/dashboard/summary")
async def dashboard_summary(current_user: dict = Depends(get_current_user)):
    producer_id = current_user["sub"]

    # 4 query independen -> dijalankan paralel lewat asyncio.gather,
    # bukan menunggu satu-satu secara berurutan.
    producer_result, config_result, top_idols_result, missions = await asyncio.gather(
        supabase_client.supabase.table("producers").select("*").eq("id", producer_id).execute(),
        supabase_client.supabase.table("app_config").select("*").eq("id", 1).execute(),
        supabase_client.supabase.table("idols").select("*").order("votes", desc=True).limit(3).execute(),
        get_or_create_today_missions(producer_id),
    )

    if not producer_result.data:
        raise HTTPException(status_code=404, detail="Producer not found")
    producer = producer_result.data[0]

    config = config_result.data[0] if config_result.data else {}

    featured_idols = [
        {"id": idol["id"], "name": idol["name"], "photo": idol["photo_url"], "rank": index}
        for index, idol in enumerate(top_idols_result.data, start=1)
    ]

    frame = await get_equipped_frame(producer_id)

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
        "equippedFrame": frame,
    }
