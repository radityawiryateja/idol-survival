import asyncio

from fastapi import APIRouter, Depends, HTTPException, Query

from app.routers.protected import get_current_user
from app.services import supabase_client
from pydantic import BaseModel

router = APIRouter()

class CastVoteRequest(BaseModel):
    quantity: int = 1

def _format_votes(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


@router.get("/idols")
async def list_idols(
    season: str | None = Query(default=None),
    filter: str | None = Query(default=None),
    q: str | None = Query(default=None),
    current_user: dict = Depends(get_current_user),
):
    query = supabase_client.supabase.table("idols").select("*").order("votes", desc=True)
    if season:
        query = query.eq("season", season)
    if q:
        query = query.ilike("name", f"%{q}%")

    rows_result, favorites_result = await asyncio.gather(
        query.execute(),
        supabase_client.supabase.table("idol_favorites")
        .select("idol_id")
        .eq("producer_id", current_user["sub"])
        .execute(),
    )
    rows = rows_result.data
    favorites = favorites_result.data
    favorited_ids = {row["idol_id"] for row in favorites}

    idols = []
    for index, row in enumerate(rows, start=1):
        idols.append(
            {
                **row,
                "rank": index,
                "favorited": row["id"] in favorited_ids,
                "votesRaw": row["votes"],
                "votes": _format_votes(row["votes"]),
                "followers": _format_votes(row["followers"]),
            }
        )

    return {"idols": idols, "total": len(idols)}


@router.post("/idols/{idol_id}/favorite")
async def toggle_favorite(idol_id: str, current_user: dict = Depends(get_current_user)):
    producer_id = current_user["sub"]
    existing = (
        await supabase_client.supabase.table("idol_favorites")
        .select("*")
        .eq("producer_id", producer_id)
        .eq("idol_id", idol_id)
        .execute()
    ).data

    if existing:
        await supabase_client.supabase.table("idol_favorites").delete().eq("producer_id", producer_id).eq(
            "idol_id", idol_id
        ).execute()
        return {"favorited": False}

    await supabase_client.supabase.table("idol_favorites").insert({"producer_id": producer_id, "idol_id": idol_id}).execute()
    return {"favorited": True}


@router.post("/idols/{idol_id}/vote")
async def cast_vote(
    idol_id: str,
    payload: CastVoteRequest,
    current_user: dict = Depends(get_current_user),
):
    if payload.quantity < 1:
        raise HTTPException(status_code=400, detail="Jumlah vote minimal 1")

    try:
        result = await supabase_client.supabase.rpc(
            "cast_vote_rpc",
            {
                "p_producer_id": current_user["sub"],
                "p_idol_id": idol_id,
                "p_quantity": payload.quantity,
            },
        ).execute()
    except Exception as exc:
        if "Insufficient vote tickets" in str(exc):
            raise HTTPException(status_code=400, detail="Saldo vote tiket kamu tidak cukup")
        raise HTTPException(status_code=400, detail="Gagal melakukan vote")

    remaining = result.data[0]["remaining_tickets"] if result.data else None
    return {"status": "ok", "remainingTickets": remaining}


@router.get("/idols/{idol_id}/card")
async def get_idol_card(idol_id: str, current_user: dict = Depends(get_current_user)):
    result = await supabase_client.supabase.table("idols").select("*").eq("id", idol_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Idol not found")

    idol = result.data[0]
    return {
        "seasonLabel": "SEASON 04 OFFICIAL",
        "projectName": "Project: Genesis",
        "level": idol.get("level", "S-RANK"),
        "photo": idol["photo_url"],
        "name": idol["name"],
        "code": idol.get("code", ""),
        "agency": idol["agency"],
        "enrollmentDate": idol.get("enrollment_date", ""),
        "specialty": idol.get("specialty", ""),
        "status": idol.get("status", "ACTIVE"),
        "qrCodeUrl": idol.get("qr_code_url", ""),
        "authToken": idol.get("auth_token", ""),
        "directorSignature": idol.get("director_signature", "S. Kang"),
    }


@router.post("/idols/{idol_id}/sync")
async def sync_id_card(idol_id: str, current_user: dict = Depends(get_current_user)):
    await supabase_client.supabase.table("idols").update({"status": "ACTIVE"}).eq("id", idol_id).execute()
    return {"status": "synced"}
