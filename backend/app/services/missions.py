import datetime

from app.services.supabase_client import supabase


def _today() -> str:
    return datetime.date.today().isoformat()


def _compute_real_progress(validation_type: str, producer_id: str, target_count: int, today: str):
    """Menghitung ulang progress dari data asli — bukan dari angka yang disimpan."""
    if validation_type == "daily_checkin":
        return 1

    if validation_type == "vote_count":
        logs = (
            supabase.table("vote_logs")
            .select("quantity")
            .eq("producer_id", producer_id)
            .gte("created_at", f"{today}T00:00:00")
            .lte("created_at", f"{today}T23:59:59")
            .execute()
            .data
        )
        return min(target_count, sum(row["quantity"] for row in logs))

    if validation_type == "referral":
        referrals_today = (
            supabase.table("producers")
            .select("id")
            .eq("referred_by", producer_id)
            .gte("created_at", f"{today}T00:00:00")
            .lte("created_at", f"{today}T23:59:59")
            .execute()
            .data
        )
        return min(target_count, len(referrals_today))

    return None  # 'manual' -> pakai progress_count yang tersimpan


async def get_or_create_today_missions(producer_id: str) -> list[dict]:
    today = _today()
    templates = supabase.table("mission_templates").select("*").order("sort_order").execute().data

    existing = (
        supabase.table("producer_missions")
        .select("*")
        .eq("producer_id", producer_id)
        .eq("mission_date", today)
        .execute()
        .data
    )
    existing_by_template = {row["mission_template_id"]: row for row in existing}

    missions = []
    for template in templates:
        record = existing_by_template.get(template["id"])
        if not record:
            record = (
                supabase.table("producer_missions")
                .insert(
                    {
                        "producer_id": producer_id,
                        "mission_template_id": template["id"],
                        "mission_date": today,
                        "progress_count": 0,
                        "status": "pending",
                    }
                )
                .execute()
                .data[0]
            )

        real_progress = _compute_real_progress(
            template["validation_type"], producer_id, template["target_count"], today
        )

        if real_progress is not None and real_progress != record["progress_count"]:
            new_status = record["status"]
            if real_progress >= template["target_count"] and record["status"] == "pending":
                new_status = "ready"
            supabase.table("producer_missions").update(
                {"progress_count": real_progress, "status": new_status}
            ).eq("id", record["id"]).execute()
            record["progress_count"] = real_progress
            record["status"] = new_status

        progress_percent = min(100, round((record["progress_count"] / template["target_count"]) * 100))
        status_text = (
            "Ready to Claim!"
            if record["status"] == "ready"
            else f"{record['progress_count']} / {template['target_count']} Completed"
        )

        missions.append(
            {
                "id": record["id"],
                "title": template["title"],
                "icon": template["icon"],
                "color": template["color"],
                "rewardIcon": template["reward_icon"],
                "rewardAmount": template["reward_amount"],
                "progressPercent": progress_percent,
                "status": record["status"],
                "statusText": status_text,
                "validationType": template["validation_type"],
            }
        )

    return missions
