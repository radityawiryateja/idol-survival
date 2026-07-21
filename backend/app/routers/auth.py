import json
import logging

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from app.schemas import SessionResponse, TelegramOidcCallback
from app.services.session import create_session_token
from app.services import supabase_client
from app.services.telegram_oidc import exchange_code_for_tokens, verify_id_token
from app.services.telegram_auth import verify_webapp_init_data

logger = logging.getLogger("idol_survival.auth")

router = APIRouter()


async def _upsert_producer(telegram_id: int, profile_fields: dict) -> dict:
    """Shared upsert logic dipakai oleh telegram_callback & webapp_login,
    supaya kedua flow login nggak divergen (dulu ada duplikasi hampir
    identik di 2 tempat)."""
    existing = await (
        supabase_client.supabase.table("producers").select("*").eq("telegram_id", telegram_id).execute()
    )

    if existing.data:
        user = existing.data[0]
        await supabase_client.supabase.table("producers").update(profile_fields).eq("id", user["id"]).execute()
        # role TIDAK ikut di-overwrite oleh profile_fields (role bukan
        # data dari Telegram) — user tetap pakai role yang sudah tersimpan.
        return user

    insert_result = await (
        supabase_client.supabase.table("producers")
        .insert({"telegram_id": telegram_id, "role": "producer", **profile_fields})
        .execute()
    )
    return insert_result.data[0]


@router.post("/telegram-callback", response_model=SessionResponse)
async def telegram_callback(payload: TelegramOidcCallback):
    try:
        tokens = await exchange_code_for_tokens(payload.code, payload.code_verifier)
        claims = await verify_id_token(tokens["id_token"])
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Telegram login failed: {exc}")

    try:
        telegram_id = claims["id"]
        profile_fields = {
            "first_name": claims.get("given_name") or claims.get("name", "Producer"),
            "last_name": claims.get("family_name"),
            "username": claims.get("preferred_username"),
            "photo_url": claims.get("picture"),
            "phone_number": claims.get("phone_number"),
        }

        user = await _upsert_producer(telegram_id, profile_fields)
        role = user.get("role", "producer")

        session_token = create_session_token(user_id=str(user["id"]), telegram_id=telegram_id, role=role)
        return SessionResponse(session_token=session_token, user=user, role=role)

    except Exception as exc:
        logger.error("telegram_callback failed: %s", exc)
        raise HTTPException(status_code=400, detail=f"Backend Error: {str(exc)}")


@router.post("/logout")
async def logout():
    # Session token JWT bersifat stateless — cukup return 200,
    # penghapusan sesungguhnya terjadi di frontend (clearSession()).
    return {"status": "ok"}


class WebAppLoginRequest(BaseModel):
    init_data: str


@router.post("/webapp-login", response_model=SessionResponse)
async def webapp_login(payload: WebAppLoginRequest):
    parsed_data = verify_webapp_init_data(payload.init_data)
    if not parsed_data:
        raise HTTPException(status_code=401, detail="Invalid Telegram Web App data")

    user_str = parsed_data.get("user")
    if not user_str:
        raise HTTPException(status_code=400, detail="No user data found")

    tg_user = json.loads(user_str)
    telegram_id = tg_user.get("id")
    profile_fields = {
        "first_name": tg_user.get("first_name", "Producer"),
        "last_name": tg_user.get("last_name"),
        "username": tg_user.get("username"),
        "photo_url": tg_user.get("photo_url"),
    }

    try:
        user = await _upsert_producer(telegram_id, profile_fields)
        role = user.get("role", "producer")

        session_token = create_session_token(user_id=str(user["id"]), telegram_id=telegram_id, role=role)
        return SessionResponse(session_token=session_token, user=user, role=role)

    except Exception as exc:
        logger.error("webapp_login failed: %s", exc)
        raise HTTPException(status_code=400, detail=f"Backend Error: {str(exc)}")
