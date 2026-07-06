import datetime

from app.services.supabase_client import supabase


def _today() -> str:
    return datetime.date.today().isoformat()


async def get_or_create_today_missions(producer_id: str) -> list[dict]:
    """
    Setiap mission_template yang aktif harus punya baris producer_missions
    untuk hari ini. Kalau belum ada, dibuatkan on-the-fly saat pertama kali
    di-fetch — jadi tidak perlu seed manual per producer.
    """
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
                "reward": f"+{template['reward_amount']} Tickets • {template['title']}",
            }
        )

    return missions
