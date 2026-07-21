from app.services import supabase_client


async def get_equipped_frame(producer_id: str) -> dict | None:
    """Return {'style', 'assetUrl', 'rarity'} kalau producer punya frame aktif, else None."""
    producer = (
        await supabase_client.supabase.table("producers")
        .select("equipped_frame_id")
        .eq("id", producer_id)
        .execute()
    ).data
    if not producer or not producer[0].get("equipped_frame_id"):
        return None

    item = (
        await supabase_client.supabase.table("shop_items")
        .select("frame_style, frame_asset_url, rarity")
        .eq("id", producer[0]["equipped_frame_id"])
        .execute()
    ).data
    if not item:
        return None

    return {
        "style": item[0]["frame_style"],
        "assetUrl": item[0]["frame_asset_url"],
        "rarity": item[0]["rarity"],
    }
