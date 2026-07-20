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


@router.get("/leaderboard")
async def get_leaderboard(current_user: dict = Depends(get_current_user)):
    idols_result, config_result = await asyncio.gather(
        supabase_client.supabase.table("idols").select("*").order("votes", desc=True).execute(),
        supabase_client.supabase.table("app_config").select("*").eq("id", 1).execute(),
    )
    idols = idols_result.data

    ranking = []
    for index, idol in enumerate(idols, start=1):
        sign = "+" if idol["trend_direction"] == "up" else "-"
        ranking.append(
            {
                "id": idol["id"],
                "rank": index,
                "name": idol["name"],
                "photo": idol["photo_url"],
                "votes": _format_votes(idol["votes"]),
                "votesFull": f"{idol['votes']:,}",
                "trend": f"{sign}{idol['trend_percent']}%",
                "trendDirection": idol["trend_direction"],
                "trendPercent": idol["trend_percent"],
                "sparkline": idol["sparkline"],
            }
        )

    config = config_result.data[0] if config_result.data else {}

    return {
        "ranking": ranking,
        "prestige": {
            "percent": config.get("prestige_percent", 0),
            "note": config.get("prestige_note", ""),
        },
    }
