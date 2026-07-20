import asyncio

from fastapi import APIRouter, Depends

from app.routers.protected import get_current_user
from app.services import supabase_client

router = APIRouter()


def _format_votes(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


@router.get("/vote/summary")
async def vote_summary(current_user: dict = Depends(get_current_user)):
    producer_id = current_user["sub"]

    producer_result, idols_result, favorites_result = await asyncio.gather(
        supabase_client.supabase.table("producers").select("*").eq("id", producer_id).execute(),
        supabase_client.supabase.table("idols").select("*").order("votes", desc=True).execute(),
        supabase_client.supabase.table("idol_favorites").select("idol_id").eq("producer_id", producer_id).execute(),
    )

    producer = producer_result.data[0]
    idols = idols_result.data
    favorited_ids = {row["idol_id"] for row in favorites_result.data}

    spotlight = idols[0] if idols else None
    spotlight_payload = None
    if spotlight:
        spotlight_payload = {
            "id": spotlight["id"],
            "name": spotlight["name"],
            "agency": spotlight["agency"],
            "photo": spotlight["photo_url"],
            "votes": _format_votes(spotlight["votes"]),
            "votesRaw": spotlight["votes"],
            "trendPercent": spotlight.get("trend_percent", 0),
            "trendDirection": spotlight.get("trend_direction", "flat"),
        }

    quick_list = [
        {
            "id": idol["id"],
            "name": idol["name"],
            "agency": idol["agency"],
            "photo": idol["photo_url"],
            "votes": _format_votes(idol["votes"]),
            "votesRaw": idol["votes"],
            "favorited": idol["id"] in favorited_ids,
        }
        # Spotlight (rank #1) sudah ditampilkan terpisah di atas, jadi
        # nggak perlu diduplikasi di list ringkas.
        for idol in idols[1:] if len(idols) > 1 else []
    ]

    return {
        "voteTickets": producer["vote_tickets"],
        "streakDays": producer["streak_days"],
        "spotlight": spotlight_payload,
        "quickList": quick_list,
    }
