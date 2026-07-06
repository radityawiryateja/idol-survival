from fastapi import APIRouter, Depends, HTTPException

from app.routers.protected import get_current_user
from app.services.missions import get_or_create_today_missions
from app.services.supabase_client import supabase

router = APIRouter()


@router.get("/tasks/summary")
async def tasks_summary(current_user: dict = Depends(get_current_user)):
    producer_result = supabase.table("producers").select("*").eq("id", current_user["sub"]).execute()
    if not producer_result.data:
        raise HTTPException(status_code=404, detail="Producer not found")
    producer = producer_result.data[0]

    config = supabase.table("app_config").select("*").eq("id", 1).execute().data
    config = config[0] if config else {}

    daily_missions = await get_or_create_today_missions(producer["id"])

    return {
        "rings": {
            "xp": {"current": producer["xp_current"], "max": producer["xp_max"]},
            "supporter": {"current": producer["supporter_points"], "max": producer["supporter_cap"]},
            "streak": {"current": producer["streak_days"], "max": 30},
        },
        "seasonPass": {"level": producer["level"], "xpToNext": producer["xp_max"] - producer["xp_current"]},
        "resetsIn": "14h 22m",
        "dailyMissions": daily_missions,
        "weeklyChest": {
            "current": config.get("weekly_chest_current", 0),
            "target": config.get("weekly_chest_target", 500),
        },
    }


@router.post("/tasks/{mission_id}/start")
async def start_mission(mission_id: str, current_user: dict = Depends(get_current_user)):
    return await _advance_mission(mission_id, current_user["sub"])


@router.post("/tasks/{mission_id}/claim")
async def claim_mission(mission_id: str, current_user: dict = Depends(get_current_user)):
    record_result = supabase.table("producer_missions").select("*").eq("id", mission_id).execute()
    if not record_result.data:
        raise HTTPException(status_code=404, detail="Mission not found")
    record = record_result.data[0]
    if record["producer_id"] != current_user["sub"]:
        raise HTTPException(status_code=403, detail="Not your mission")

    template = (
        supabase.table("mission_templates").select("*").eq("id", record["mission_template_id"]).execute().data[0]
    )

    supabase.table("producer_missions").update({"status": "claimed"}).eq("id", mission_id).execute()

    current_diamonds = (
        supabase.table("producers").select("diamonds").eq("id", current_user["sub"]).execute().data[0]["diamonds"]
    )
    supabase.table("producers").update({"diamonds": current_diamonds + template["reward_amount"]}).eq(
        "id", current_user["sub"]
    ).execute()

    return {
        "status": "claimed",
        "statusText": f"{template['target_count']} / {template['target_count']} Completed",
        "progressPercent": 100,
    }


async def _advance_mission(mission_id: str, producer_id: str) -> dict:
    record_result = supabase.table("producer_missions").select("*").eq("id", mission_id).execute()
    if not record_result.data:
        raise HTTPException(status_code=404, detail="Mission not found")
    record = record_result.data[0]
    if record["producer_id"] != producer_id:
        raise HTTPException(status_code=403, detail="Not your mission")

    template = (
        supabase.table("mission_templates").select("*").eq("id", record["mission_template_id"]).execute().data[0]
    )

    new_progress = min(template["target_count"], record["progress_count"] + 1)
    new_status = "ready" if new_progress >= template["target_count"] else "pending"

    supabase.table("producer_missions").update(
        {"progress_count": new_progress, "status": new_status}
    ).eq("id", mission_id).execute()

    progress_percent = round((new_progress / template["target_count"]) * 100)
    status_text = (
        "Ready to Claim!" if new_status == "ready" else f"{new_progress} / {template['target_count']} Completed"
    )

    return {"status": new_status, "statusText": status_text, "progressPercent": progress_percent}
