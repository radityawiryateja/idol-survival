from fastapi import APIRouter, Depends, HTTPException

from app.routers.protected import get_current_user
from app.services.supabase_client import supabase

router = APIRouter()


@router.get("/rewards")
async def list_rewards(current_user: dict = Depends(get_current_user)):
    rewards = (
        supabase.table("rewards")
        .select("*")
        .eq("active", True)
        .order("sort_order")
        .execute()
        .data
    )

    producer = (
        supabase.table("producers")
        .select("diamonds")
        .eq("id", current_user["sub"])
        .execute()
        .data
    )
    diamonds = producer[0]["diamonds"] if producer else 0

    return {
        "diamonds": diamonds,
        "rewards": [
            {
                "id": r["id"],
                "title": r["title"],
                "description": r["description"],
                "icon": r["icon"],
                "color": r["color"],
                "category": r["category"],
                "costDiamonds": r["cost_diamonds"],
                "inStock": r["stock"] is None or r["stock"] > 0,
            }
            for r in rewards
        ],
    }


@router.post("/rewards/{reward_id}/redeem")
async def redeem_reward(reward_id: str, current_user: dict = Depends(get_current_user)):
    try:
        result = supabase.rpc(
            "redeem_reward_rpc",
            {"p_producer_id": current_user["sub"], "p_reward_id": reward_id},
        ).execute()
    except Exception as exc:
        message = str(exc)
        if "Insufficient diamonds" in message:
            raise HTTPException(status_code=400, detail="Diamond kamu tidak cukup")
        if "out of stock" in message:
            raise HTTPException(status_code=400, detail="Reward ini sudah habis")
        raise HTTPException(status_code=400, detail="Gagal menukar reward")

    row = result.data[0] if result.data else None
    return {
        "status": "ok",
        "remainingDiamonds": row["remaining_diamonds"] if row else None,
    }
