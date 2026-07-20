import asyncio
import datetime

from fastapi import APIRouter, Depends, HTTPException

from app.routers.protected import get_current_user
from app.services import supabase_client

router = APIRouter()


def _status_for(start_at: str, end_at: str) -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    start = datetime.datetime.fromisoformat(start_at.replace("Z", "+00:00"))
    end = datetime.datetime.fromisoformat(end_at.replace("Z", "+00:00"))
    if now < start:
        return "upcoming"
    if now > end:
        return "ended"
    return "active"


def _countdown_label(end_at: str) -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    end = datetime.datetime.fromisoformat(end_at.replace("Z", "+00:00"))
    delta = end - now
    if delta.total_seconds() <= 0:
        return "Ended"
    days = delta.days
    hours = delta.seconds // 3600
    if days > 0:
        return f"{days}d {hours}h left"
    minutes = (delta.seconds % 3600) // 60
    return f"{hours}h {minutes}m left"


async def _compute_progress(event: dict, producer_id: str) -> int:
    """
    Event kategori 'voting' progress-nya dihitung ulang dari vote_logs asli
    (sama filosofinya kayak get_or_create_today_missions di missions.py) —
    bukan angka yang cuma disimpan, biar nggak bisa dimanipulasi client.
    Kategori lain ('seasonal', 'community') pakai progress_count yang
    tersimpan di producer_event_progress (diupdate dari tempat lain, mis.
    webhook atau job terpisah).
    """
    if event["category"] != "voting":
        stored = (
            await supabase_client.supabase.table("producer_event_progress")
            .select("progress_count")
            .eq("producer_id", producer_id)
            .eq("event_id", event["id"])
            .execute()
        ).data
        return stored[0]["progress_count"] if stored else 0

    logs = (
        await supabase_client.supabase.table("vote_logs")
        .select("quantity")
        .eq("producer_id", producer_id)
        .gte("created_at", event["start_at"])
        .lte("created_at", event["end_at"])
        .execute()
    ).data
    return sum(row["quantity"] for row in logs)


async def _sync_progress(producer_id: str, event_id: str, progress: int) -> None:
    existing = (
        await supabase_client.supabase.table("producer_event_progress")
        .select("progress_count")
        .eq("producer_id", producer_id)
        .eq("event_id", event_id)
        .execute()
    ).data

    if existing:
        if existing[0]["progress_count"] != progress:
            await supabase_client.supabase.table("producer_event_progress").update(
                {"progress_count": progress, "updated_at": "now()"}
            ).eq("producer_id", producer_id).eq("event_id", event_id).execute()
    else:
        await supabase_client.supabase.table("producer_event_progress").insert(
            {"producer_id": producer_id, "event_id": event_id, "progress_count": progress}
        ).execute()


async def _build_event_payload(event: dict, producer_id: str, include_milestones: bool = True) -> dict:
    progress = await _compute_progress(event, producer_id)
    await _sync_progress(producer_id, event["id"], progress)

    payload = {
        "id": event["id"],
        "title": event["title"],
        "subtitle": event.get("subtitle"),
        "description": event.get("description"),
        "bannerImage": event.get("banner_image"),
        "category": event["category"],
        "color": event["color"],
        "progressLabel": event["progress_label"],
        "status": _status_for(event["start_at"], event["end_at"]),
        "countdown": _countdown_label(event["end_at"]),
        "startAt": event["start_at"],
        "endAt": event["end_at"],
        "progress": progress,
    }

    if not include_milestones:
        last_milestone = (
            await supabase_client.supabase.table("event_milestones")
            .select("target_count")
            .eq("event_id", event["id"])
            .order("target_count", desc=True)
            .limit(1)
            .execute()
        ).data
        payload["finalTarget"] = last_milestone[0]["target_count"] if last_milestone else 0

    if include_milestones:
        milestones = (
            await supabase_client.supabase.table("event_milestones")
            .select("*")
            .eq("event_id", event["id"])
            .order("sort_order")
            .execute()
        ).data

        claimed_ids = set()
        if milestones:
            claims = (
                await supabase_client.supabase.table("producer_event_milestone_claims")
                .select("milestone_id")
                .eq("producer_id", producer_id)
                .in_("milestone_id", [m["id"] for m in milestones])
                .execute()
            ).data
            claimed_ids = {c["milestone_id"] for c in claims}

        payload["milestones"] = [
            {
                "id": m["id"],
                "title": m["title"],
                "icon": m["icon"],
                "targetCount": m["target_count"],
                "rewardDiamonds": m["reward_diamonds"],
                "rewardVoteTickets": m["reward_vote_tickets"],
                "progressPercent": min(100, round((progress / m["target_count"]) * 100)) if m["target_count"] else 100,
                "claimed": m["id"] in claimed_ids,
                "claimable": progress >= m["target_count"] and m["id"] not in claimed_ids,
            }
            for m in milestones
        ]
        payload["totalMilestones"] = len(milestones)
        payload["claimedMilestones"] = len(claimed_ids)

    return payload


@router.get("/events")
async def list_events(current_user: dict = Depends(get_current_user)):
    producer_id = current_user["sub"]

    events = (
        await supabase_client.supabase.table("events")
        .select("*")
        .eq("active", True)
        .order("sort_order")
        .order("start_at")
        .execute()
    ).data

    payloads = await asyncio.gather(
        *(_build_event_payload(event, producer_id, include_milestones=False) for event in events)
    )

    # Urutkan: active dulu, lalu upcoming, lalu ended paling belakang.
    status_order = {"active": 0, "upcoming": 1, "ended": 2}
    payloads = sorted(payloads, key=lambda e: status_order.get(e["status"], 3))

    return {"events": payloads}


@router.get("/events/{event_id}")
async def get_event_detail(event_id: str, current_user: dict = Depends(get_current_user)):
    result = await supabase_client.supabase.table("events").select("*").eq("id", event_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Event not found")

    event = result.data[0]
    payload = await _build_event_payload(event, current_user["sub"], include_milestones=True)
    return payload


@router.post("/events/{event_id}/milestones/{milestone_id}/claim")
async def claim_event_milestone(
    event_id: str, milestone_id: str, current_user: dict = Depends(get_current_user)
):
    try:
        result = await supabase_client.supabase.rpc(
            "claim_event_milestone_rpc",
            {"p_producer_id": current_user["sub"], "p_milestone_id": milestone_id},
        ).execute()
    except Exception as exc:
        message = str(exc)
        if "already claimed" in message:
            raise HTTPException(status_code=400, detail="Reward ini sudah pernah diklaim")
        if "not eligible" in message:
            raise HTTPException(status_code=400, detail="Progress kamu belum cukup untuk milestone ini")
        raise HTTPException(status_code=400, detail="Gagal mengklaim reward event")

    row = result.data[0] if result.data else None
    return {
        "status": "ok",
        "remainingDiamonds": row["remaining_diamonds"] if row else None,
        "remainingTickets": row["remaining_tickets"] if row else None,
    }
