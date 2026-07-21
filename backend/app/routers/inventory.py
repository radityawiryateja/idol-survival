from fastapi import APIRouter, Depends, HTTPException

from app.routers.protected import get_current_user
from app.services.frames import get_equipped_frame
from app.services import supabase_client

router = APIRouter()


@router.get("/inventory/avatars")
async def list_owned_avatars(current_user: dict = Depends(get_current_user)):
    producer_id = current_user["sub"]

    producer_result = (
        await supabase_client.supabase.table("producers")
        .select("photo_url, equipped_avatar_url")
        .eq("id", producer_id)
        .execute()
    )
    if not producer_result.data:
        raise HTTPException(status_code=404, detail="Producer not found")
    producer = producer_result.data[0]

    owned = (
        await supabase_client.supabase.table("producer_inventory")
        .select("item_id, shop_items(id, title, asset_url, icon, color)")
        .eq("producer_id", producer_id)
        .execute()
    ).data

    default_avatar = producer["photo_url"]
    equipped_url = producer.get("equipped_avatar_url") or default_avatar

    avatars = [
        {
            "id": row["shop_items"]["id"],
            "title": row["shop_items"]["title"],
            "assetUrl": row["shop_items"]["asset_url"],
            "equipped": row["shop_items"]["asset_url"] == producer.get("equipped_avatar_url"),
        }
        for row in owned
        if row.get("shop_items") and row["shop_items"].get("asset_url")
    ]

    return {
        "defaultAvatarUrl": default_avatar,
        "equippedUrl": equipped_url,
        "usingDefault": not producer.get("equipped_avatar_url"),
        "avatars": avatars,
    }


@router.post("/inventory/avatars/{item_id}/equip")
async def equip_avatar(item_id: str, current_user: dict = Depends(get_current_user)):
    producer_id = current_user["sub"]

    owns = (
        await supabase_client.supabase.table("producer_inventory")
        .select("item_id")
        .eq("producer_id", producer_id)
        .eq("item_id", item_id)
        .execute()
    ).data
    if not owns:
        raise HTTPException(status_code=403, detail="Kamu belum memiliki avatar ini")

    item_result = (
        await supabase_client.supabase.table("shop_items").select("asset_url").eq("id", item_id).execute()
    )
    if not item_result.data or not item_result.data[0].get("asset_url"):
        raise HTTPException(status_code=404, detail="Avatar tidak ditemukan")

    asset_url = item_result.data[0]["asset_url"]
    await supabase_client.supabase.table("producers").update(
        {"equipped_avatar_url": asset_url}
    ).eq("id", producer_id).execute()

    return {"status": "ok", "equippedUrl": asset_url}


@router.post("/inventory/avatars/reset")
async def reset_avatar(current_user: dict = Depends(get_current_user)):
    """Balik ke foto profil Telegram asli (photo_url)."""
    await supabase_client.supabase.table("producers").update(
        {"equipped_avatar_url": None}
    ).eq("id", current_user["sub"]).execute()
    return {"status": "ok"}

@router.get("/inventory/frames")
async def list_owned_frames(current_user: dict = Depends(get_current_user)):
    producer_id = current_user["sub"]

    owned = (
        await supabase_client.supabase.table("producer_inventory")
        .select("item_id, shop_items(id, title, frame_style, frame_asset_url, rarity)")
        .eq("producer_id", producer_id)
        .execute()
    ).data

    equipped = await get_equipped_frame(producer_id)

    frames = [
        {
            "id": row["shop_items"]["id"],
            "title": row["shop_items"]["title"],
            "frameStyle": row["shop_items"]["frame_style"],
            "frameAssetUrl": row["shop_items"]["frame_asset_url"],
            "rarity": row["shop_items"]["rarity"],
            "equipped": equipped is not None and equipped["style"] == row["shop_items"]["frame_style"]
            and row["shop_items"]["id"] == (
                (await supabase_client.supabase.table("producers").select("equipped_frame_id").eq("id", producer_id).execute()).data[0]["equipped_frame_id"]
            ),
        }
        for row in owned
        if row.get("shop_items") and row["shop_items"].get("frame_style") not in (None, "none")
    ]

    return {"equipped": equipped, "frames": frames}


@router.post("/inventory/frames/{item_id}/equip")
async def equip_frame(item_id: str, current_user: dict = Depends(get_current_user)):
    producer_id = current_user["sub"]
    owns = (
        await supabase_client.supabase.table("producer_inventory")
        .select("item_id")
        .eq("producer_id", producer_id)
        .eq("item_id", item_id)
        .execute()
    ).data
    if not owns:
        raise HTTPException(status_code=403, detail="Kamu belum memiliki frame ini")

    await supabase_client.supabase.table("producers").update(
        {"equipped_frame_id": item_id}
    ).eq("id", producer_id).execute()

    return {"status": "ok"}


@router.post("/inventory/frames/reset")
async def reset_frame(current_user: dict = Depends(get_current_user)):
    await supabase_client.supabase.table("producers").update(
        {"equipped_frame_id": None}
    ).eq("id", current_user["sub"]).execute()
    return {"status": "ok"}
