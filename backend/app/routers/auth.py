from fastapi import APIRouter, HTTPException

from app.schemas import SessionResponse, TelegramAuthPayload
from app.services.session import create_session_token
from app.services.supabase_client import supabase
from app.services.telegram_auth import verify_telegram_auth

router = APIRouter()


@router.post("/telegram-callback", response_model=SessionResponse)
async def telegram_callback(payload: TelegramAuthPayload):
    """
    Receives the user object produced by the Telegram Login Widget
    (forwarded from the frontend), validates it, upserts the producer
    in Supabase, and returns a session token for the frontend to store.
    """
    data = payload.model_dump()

    if not verify_telegram_auth(data):
        raise HTTPException(status_code=401, detail="Invalid Telegram authentication data")

    telegram_id = payload.id

    existing = (
        supabase.table("producers")
        .select("*")
        .eq("telegram_id", telegram_id)
        .execute()
    )

    if existing.data:
        user = existing.data[0]
        # Keep profile info fresh on every login
        supabase.table("producers").update(
            {
                "first_name": payload.first_name,
                "last_name": payload.last_name,
                "username": payload.username,
                "photo_url": payload.photo_url,
            }
        ).eq("id", user["id"]).execute()
    else:
        insert_result = (
            supabase.table("producers")
            .insert(
                {
                    "telegram_id": telegram_id,
                    "first_name": payload.first_name,
                    "last_name": payload.last_name,
                    "username": payload.username,
                    "photo_url": payload.photo_url,
                }
            )
            .execute()
        )
        user = insert_result.data[0]

    session_token = create_session_token(user_id=str(user["id"]), telegram_id=telegram_id)

    return SessionResponse(session_token=session_token, user=user)
