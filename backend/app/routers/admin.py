import asyncio

from fastapi import APIRouter, Depends

from app.services.rbac import require_role
from app.services import supabase_client

router = APIRouter()


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


@router.patch("/admin/producers/{producer_id}/role")
async def set_producer_role(producer_id: str, role: str, current_user: dict = Depends(require_role("admin"))):
    if role not in {"producer", "idol", "admin"}:
        return {"status": "error", "detail": "Role tidak valid"}

    await supabase_client.supabase.table("producers").update({"role": role}).eq("id", producer_id).execute()
    return {"status": "ok"}
