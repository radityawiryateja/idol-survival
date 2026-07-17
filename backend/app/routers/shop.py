from fastapi import APIRouter, Depends, HTTPException

from app.routers.protected import get_current_user
from app.services.supabase_client import supabase

router = APIRouter()


@router.get("/shop")
async def list_shop_items(current_user: dict = Depends(get_current_user)):
    items = (
        supabase.table("shop_items")
        .select("*")
        .eq("active", True)
        .order("sort_order")
        .execute()
        .data
    )

    producer_result = (
        supabase.table("producers")
        .select("diamonds, vote_tickets")
        .eq("id", current_user["sub"])
        .execute()
        .data
    )
    producer = producer_result[0] if producer_result else {"diamonds": 0, "vote_tickets": 0}

    return {
        "diamonds": producer["diamonds"],
        "voteTickets": producer["vote_tickets"],
        "items": [
            {
                "id": item["id"],
                "title": item["title"],
                "description": item["description"],
                "icon": item["icon"],
                "color": item["color"],
                "category": item["category"],
                "costDiamonds": item["cost_diamonds"],
                "inStock": item["stock"] is None or item["stock"] > 0,
            }
            for item in items
        ],
    }


@router.post("/shop/{item_id}/purchase")
async def purchase_shop_item(item_id: str, current_user: dict = Depends(get_current_user)):
    try:
        result = supabase.rpc(
            "purchase_shop_item_rpc",
            {"p_producer_id": current_user["sub"], "p_item_id": item_id},
        ).execute()
    except Exception as exc:
        message = str(exc)
        if "Insufficient diamonds" in message:
            raise HTTPException(status_code=400, detail="Diamond kamu tidak cukup")
        if "out of stock" in message:
            raise HTTPException(status_code=400, detail="Item ini sudah habis")
        raise HTTPException(status_code=400, detail="Gagal melakukan pembelian")

    row = result.data[0] if result.data else None
    return {
        "status": "ok",
        "remainingDiamonds": row["remaining_diamonds"] if row else None,
        "remainingTickets": row["remaining_tickets"] if row else None,
    }
