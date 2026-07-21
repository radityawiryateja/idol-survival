from fastapi import APIRouter, Depends, HTTPException

from app.services.rbac import require_role
from app.services import supabase_client

router = APIRouter()


async def _idol_for_producer(producer_id: str) -> dict:
    """Menghubungkan akun producer ber-role 'idol' ke baris `idols` miliknya,
    lewat kolom `producers.linked_idol_id` (tambahkan kolom ini kalau belum
    ada) — bukan lewat telegram_admin_chat_id, supaya idol tetap bisa login
    dari akun Telegram pribadinya sendiri, terpisah dari akun broadcast bot.
    """
    result = await supabase_client.supabase.table("idols").select("*").eq(
        "linked_producer_id", producer_id
    ).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Akun ini belum ditautkan ke profil idol manapun")
    return result.data[0]


@router.get("/idol-panel/me")
async def get_my_idol_profile(current_user: dict = Depends(require_role("idol"))):
    idol = await _idol_for_producer(current_user["sub"])
    return idol


@router.get("/idol-panel/messages")
async def get_my_fan_messages(current_user: dict = Depends(require_role("idol"))):
    idol = await _idol_for_producer(current_user["sub"])
    messages = (
        await supabase_client.supabase.table("idol_private_messages")
        .select("*")
        .eq("idol_id", idol["id"])
        .order("created_at", desc=True)
        .limit(50)
        .execute()
    ).data
    return {"messages": messages}
