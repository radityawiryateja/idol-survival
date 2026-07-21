from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.routers.protected import get_current_user
from app.services import supabase_client

router = APIRouter()

DEFAULT_NOTIFICATION_PREFS = {
    "voteReminders": True,
    "missionReminders": True,
    "liveBroadcastAlerts": True,
    "chatMessageAlerts": True,
}
DEFAULT_APPEARANCE_PREFS = {
    "reduceMotion": False,
    "holographicEffects": True,
}


async def _get_or_create_settings_row(producer_id: str) -> dict:
    existing = (
        await supabase_client.supabase.table("producer_settings")
        .select("*")
        .eq("producer_id", producer_id)
        .execute()
    ).data

    if existing:
        return existing[0]

    inserted = (
        await supabase_client.supabase.table("producer_settings")
        .insert(
            {
                "producer_id": producer_id,
                "notification_prefs": DEFAULT_NOTIFICATION_PREFS,
                "appearance_prefs": DEFAULT_APPEARANCE_PREFS,
            }
        )
        .execute()
    ).data
    return inserted[0]


# ------------------------- Account -------------------------

@router.get("/settings/account")
async def get_account_settings(current_user: dict = Depends(get_current_user)):
    result = await supabase_client.supabase.table("producers").select("*").eq("id", current_user["sub"]).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Producer not found")

    producer = result.data[0]
    return {
        "telegramUsername": producer.get("username"),
        "firstName": producer["first_name"],
        "lastName": producer.get("last_name"),
        "displayName": producer.get("display_name") or producer["first_name"],
        "bio": producer.get("bio") or "",
        "avatarUrl": producer.get("equipped_avatar_url") or producer.get("photo_url"),
    }


class UpdateAccountRequest(BaseModel):
    displayName: str
    bio: str = ""


@router.patch("/settings/account")
async def update_account_settings(
    payload: UpdateAccountRequest, current_user: dict = Depends(get_current_user)
):
    display_name = payload.displayName.strip()
    if not display_name:
        raise HTTPException(status_code=400, detail="Nama tampilan tidak boleh kosong")
    if len(display_name) > 50:
        raise HTTPException(status_code=400, detail="Nama tampilan maksimal 50 karakter")
    if len(payload.bio) > 200:
        raise HTTPException(status_code=400, detail="Bio maksimal 200 karakter")

    await supabase_client.supabase.table("producers").update(
        {"display_name": display_name, "bio": payload.bio.strip()}
    ).eq("id", current_user["sub"]).execute()

    return {"status": "ok"}


# ------------------------- Notifications -------------------------

@router.get("/settings/notifications")
async def get_notification_settings(current_user: dict = Depends(get_current_user)):
    row = await _get_or_create_settings_row(current_user["sub"])
    return row["notification_prefs"]


class UpdateNotificationRequest(BaseModel):
    voteReminders: bool
    missionReminders: bool
    liveBroadcastAlerts: bool
    chatMessageAlerts: bool


@router.patch("/settings/notifications")
async def update_notification_settings(
    payload: UpdateNotificationRequest, current_user: dict = Depends(get_current_user)
):
    await _get_or_create_settings_row(current_user["sub"])  # pastikan row ada
    await supabase_client.supabase.table("producer_settings").update(
        {"notification_prefs": payload.model_dump(), "updated_at": "now()"}
    ).eq("producer_id", current_user["sub"]).execute()
    return {"status": "ok"}


# ------------------------- Appearance -------------------------

@router.get("/settings/appearance")
async def get_appearance_settings(current_user: dict = Depends(get_current_user)):
    row = await _get_or_create_settings_row(current_user["sub"])
    return row["appearance_prefs"]


class UpdateAppearanceRequest(BaseModel):
    reduceMotion: bool
    holographicEffects: bool


@router.patch("/settings/appearance")
async def update_appearance_settings(
    payload: UpdateAppearanceRequest, current_user: dict = Depends(get_current_user)
):
    await _get_or_create_settings_row(current_user["sub"])
    await supabase_client.supabase.table("producer_settings").update(
        {"appearance_prefs": payload.model_dump(), "updated_at": "now()"}
    ).eq("producer_id", current_user["sub"]).execute()
    return {"status": "ok"}
