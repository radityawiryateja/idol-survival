from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.bot import forward_reply_to_idol
from app.routers.protected import get_current_user
from app.services.supabase_client import supabase

router = APIRouter()


@router.get("/talks/rooms")
async def list_talk_rooms(current_user: dict = Depends(get_current_user)):
    idols = supabase.table("idols").select("id, name, photo_url").order("name").execute().data

    rooms = []
    for idol in idols:
        last_broadcast = (
            supabase.table("idol_broadcasts")
            .select("content, media_type, created_at")
            .eq("idol_id", idol["id"])
            .order("created_at", desc=True)
            .limit(1)
            .execute()
            .data
        )
        last_private = (
            supabase.table("idol_private_messages")
            .select("content, media_type, created_at")
            .eq("idol_id", idol["id"])
            .eq("producer_id", current_user["sub"])
            .order("created_at", desc=True)
            .limit(1)
            .execute()
            .data
        )

        candidates = [m for m in (last_broadcast + last_private)]
        candidates.sort(key=lambda m: m["created_at"], reverse=True)
        last_message = candidates[0] if candidates else None

        rooms.append(
            {
                "idolId": idol["id"],
                "name": idol["name"],
                "photo": idol["photo_url"],
                "lastMessagePreview": (
                    "📷 Photo"
                    if last_message and last_message["media_type"] != "text"
                    else (last_message["content"] if last_message else "Belum ada pesan")
                ),
                "lastMessageAt": last_message["created_at"] if last_message else None,
            }
        )

    rooms.sort(key=lambda r: r["lastMessageAt"] or "", reverse=True)
    return {"rooms": rooms}


@router.get("/talks/{idol_id}/messages")
async def get_talk_messages(idol_id: str, current_user: dict = Depends(get_current_user)):
    broadcasts = (
        supabase.table("idol_broadcasts").select("*").eq("idol_id", idol_id).order("created_at").execute().data
    )
    private_messages = (
        supabase.table("idol_private_messages")
        .select("*")
        .eq("idol_id", idol_id)
        .eq("producer_id", current_user["sub"])
        .order("created_at")
        .execute()
        .data
    )

    timeline = [
        {
            "id": b["id"],
            "sender": "idol",
            "scope": "broadcast",
            "content": b["content"],
            "mediaUrl": b["media_url"],
            "mediaType": b["media_type"],
            "createdAt": b["created_at"],
        }
        for b in broadcasts
    ] + [
        {
            "id": m["id"],
            "sender": m["sender"],
            "scope": "private",
            "content": m["content"],
            "mediaUrl": m["media_url"],
            "mediaType": m["media_type"],
            "createdAt": m["created_at"],
        }
        for m in private_messages
    ]
    timeline.sort(key=lambda m: m["createdAt"])
    return {"messages": timeline}


class SendMessageRequest(BaseModel):
    content: str


@router.post("/talks/{idol_id}/messages")
async def send_talk_message(
    idol_id: str, payload: SendMessageRequest, current_user: dict = Depends(get_current_user)
):
    if not payload.content.strip():
        raise HTTPException(status_code=400, detail="Pesan tidak boleh kosong")

    idol_result = supabase.table("idols").select("*").eq("id", idol_id).execute()
    if not idol_result.data:
        raise HTTPException(status_code=404, detail="Idol not found")
    idol = idol_result.data[0]

    producer = (
        supabase.table("producers")
        .select("first_name, username")
        .eq("id", current_user["sub"])
        .execute()
        .data[0]
    )

    inserted = (
        supabase.table("idol_private_messages")
        .insert(
            {
                "idol_id": idol_id,
                "producer_id": current_user["sub"],
                "sender": "user",
                "content": payload.content,
                "media_type": "text",
            }
        )
        .execute()
        .data[0]
    )

    if idol.get("telegram_admin_chat_id"):
        label = f"@{producer['username']}" if producer.get("username") else producer["first_name"]
        forwarded_text = f"💬 {producer['first_name']} ({label}):\n{payload.content}"
        try:
            telegram_message_id = await forward_reply_to_idol(idol["telegram_admin_chat_id"], forwarded_text)
            if telegram_message_id:
                supabase.table("idol_private_messages").update(
                    {"telegram_message_id": telegram_message_id}
                ).eq("id", inserted["id"]).execute()
        except Exception as exc:
            # Pesan tetap tersimpan di DB meski forward ke Telegram gagal
            print(f"Failed to forward message to Telegram: {exc}")

    return {"status": "ok", "messageId": inserted["id"]}
