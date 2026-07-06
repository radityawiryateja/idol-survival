from fastapi import APIRouter, HTTPException

from app.schemas import SessionResponse, TelegramOidcCallback
from app.services.session import create_session_token
from app.services.supabase_client import supabase
from app.services.telegram_oidc import exchange_code_for_tokens, verify_id_token

router = APIRouter()


@router.post("/api/telegram-callback", response_model=SessionResponse)
async def telegram_callback(payload: TelegramOidcCallback):
    try:
        tokens = await exchange_code_for_tokens(payload.code, payload.code_verifier)
        claims = await verify_id_token(tokens["id_token"])
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Telegram login failed: {exc}")

    telegram_id = claims["id"]
    first_name = claims.get("given_name") or claims.get("name", "Producer")
    last_name = claims.get("family_name")
    username = claims.get("preferred_username")
    photo_url = claims.get("picture")
    phone_number = claims.get("phone_number")

    existing = (
        supabase.table("producers").select("*").eq("telegram_id", telegram_id).execute()
    )

    profile_fields = {
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
        "photo_url": photo_url,
        "phone_number": phone_number,
    }

    if existing.data:
        user = existing.data[0]
        supabase.table("producers").update(profile_fields).eq("id", user["id"]).execute()
    else:
        insert_result = (
            supabase.table("producers")
            .insert({"telegram_id": telegram_id, **profile_fields})
            .execute()
        )
        user = insert_result.data[0]

    session_token = create_session_token(user_id=str(user["id"]), telegram_id=telegram_id)
    return SessionResponse(session_token=session_token, user=user)
