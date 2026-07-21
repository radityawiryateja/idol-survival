# app/routers/admin.py
import asyncio
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.services.rbac import require_role
from app.services import supabase_client

router = APIRouter()


# ------------------------- Overview -------------------------

@router.get("/admin/overview")
async def admin_overview(current_user: dict = Depends(require_role("admin"))):
    producers_result, idols_result = await asyncio.gather(
        supabase_client.supabase.table("producers").select("id", count="exact").execute(),
        supabase_client.supabase.table("idols").select("id", count="exact").execute(),
    )
    return {
        "totalProducers": producers_result.count or 0,
        "totalIdols": idols_result.count or 0,
    }


# ------------------------- Producers & roles -------------------------

@router.get("/admin/producers")
async def search_producers(q: str = "", current_user: dict = Depends(require_role("admin"))):
    query = supabase_client.supabase.table("producers").select(
        "id, telegram_id, first_name, last_name, username, role, photo_url"
    ).order("first_name").limit(20)

    if q:
        # ilike di beberapa kolom sekaligus lewat or_() Supabase
        query = query.or_(f"first_name.ilike.%{q}%,username.ilike.%{q}%,telegram_id.eq.{q if q.isdigit() else 0}")

    result = await query.execute()
    return {"producers": result.data}


class UpdateRoleRequest(BaseModel):
    role: str


@router.patch("/admin/producers/{producer_id}/role")
async def set_producer_role(
    producer_id: str, payload: UpdateRoleRequest, current_user: dict = Depends(require_role("admin"))
):
    if payload.role not in {"producer", "idol", "admin"}:
        raise HTTPException(status_code=400, detail="Role tidak valid")

    # Admin tidak boleh menurunkan role dirinya sendiri secara tidak
    # sengaja dari panel ini dan kehilangan akses.
    if producer_id == current_user["sub"] and payload.role != "admin":
        raise HTTPException(status_code=400, detail="Tidak bisa mengubah role akun sendiri")

    await supabase_client.supabase.table("producers").update({"role": payload.role}).eq(
        "id", producer_id
    ).execute()
    return {"status": "ok"}


# ------------------------- Shop items -------------------------

class ShopItemPayload(BaseModel):
    title: str
    description: str = ""
    icon: str = "shopping_bag"
    color: str = "primary"
    category: str  # 'tickets' | 'boosts' | 'cosmetics' | 'avatar'
    cost_diamonds: int
    stock: Optional[int] = None  # null = unlimited
    asset_url: Optional[str] = None  # wajib diisi kalau category == 'avatar'
    sort_order: int = 0
    active: bool = True


class ShopItemUpdatePayload(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    category: Optional[str] = None
    cost_diamonds: Optional[int] = None
    stock: Optional[int] = None
    asset_url: Optional[str] = None
    sort_order: Optional[int] = None
    active: Optional[bool] = None


VALID_CATEGORIES = {"tickets", "boosts", "cosmetics", "avatar"}


@router.get("/admin/shop-items")
async def list_all_shop_items(current_user: dict = Depends(require_role("admin"))):
    # Beda dari GET /shop biasa: ini ambil SEMUA item (termasuk non-active)
    # supaya admin bisa lihat & nyalakan lagi item yang di-nonaktifkan.
    result = await supabase_client.supabase.table("shop_items").select("*").order("sort_order").execute()
    return {"items": result.data}


@router.post("/admin/shop-items")
async def create_shop_item(payload: ShopItemPayload, current_user: dict = Depends(require_role("admin"))):
    if payload.category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail="Kategori tidak valid")
    if payload.category == "avatar" and not payload.asset_url:
        raise HTTPException(status_code=400, detail="Item avatar wajib punya asset_url (URL gambar)")

    inserted = (
        await supabase_client.supabase.table("shop_items").insert(payload.model_dump()).execute()
    ).data
    return {"status": "ok", "item": inserted[0] if inserted else None}


@router.patch("/admin/shop-items/{item_id}")
async def update_shop_item(
    item_id: str, payload: ShopItemUpdatePayload, current_user: dict = Depends(require_role("admin"))
):
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="Tidak ada perubahan yang dikirim")
    if "category" in updates and updates["category"] not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail="Kategori tidak valid")

    await supabase_client.supabase.table("shop_items").update(updates).eq("id", item_id).execute()
    return {"status": "ok"}


# Tidak ada hard-delete dengan sengaja: shop_items direferensikan oleh
# producer_inventory (avatar yang sudah dimiliki producer). Menghapus
# barisnya akan ikut menghapus kepemilikan avatar orang lain lewat FK
# cascade. Untuk "menghapus" dari etalase, nonaktifkan lewat PATCH
# {"active": false} di atas.


# ------------------------- Idol linking -------------------------

@router.get("/admin/idols")
async def list_idols_for_admin(current_user: dict = Depends(require_role("admin"))):
    result = await supabase_client.supabase.table("idols").select(
        "id, name, agency, photo_url, linked_producer_id, telegram_admin_chat_id"
    ).order("name").execute()
    return {"idols": result.data}


class LinkIdolRequest(BaseModel):
    producer_id: str


@router.patch("/admin/idols/{idol_id}/link")
async def link_idol_account(
    idol_id: str, payload: LinkIdolRequest, current_user: dict = Depends(require_role("admin"))
):
    producer = (
        await supabase_client.supabase.table("producers").select("id, role").eq("id", payload.producer_id).execute()
    ).data
    if not producer:
        raise HTTPException(status_code=404, detail="Producer tidak ditemukan")

    # Auto-naikkan role ke 'idol' kalau belum, supaya admin tidak perlu
    # bolak-balik ke tab Producers untuk 2 langkah terpisah.
    if producer[0]["role"] != "idol":
        await supabase_client.supabase.table("producers").update({"role": "idol"}).eq(
            "id", payload.producer_id
        ).execute()

    await supabase_client.supabase.table("idols").update(
        {"linked_producer_id": payload.producer_id}
    ).eq("id", idol_id).execute()
    return {"status": "ok"}


@router.patch("/admin/idols/{idol_id}/unlink")
async def unlink_idol_account(idol_id: str, current_user: dict = Depends(require_role("admin"))):
    await supabase_client.supabase.table("idols").update(
        {"linked_producer_id": None}
    ).eq("id", idol_id).execute()
    return {"status": "ok"}
