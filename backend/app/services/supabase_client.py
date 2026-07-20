from supabase import acreate_client, AsyncClient

from app.config import settings

# Diisi saat startup lewat init_supabase() di lifespan main.py.
# Modul-modul lain tetap import `supabase` seperti biasa, tapi sekarang
# nilainya adalah AsyncClient dan tiap `.execute()` HARUS di-await.
#
# Uses the service-role key because this client runs on the backend only.
# Never ship the service-role key to the frontend.
supabase: AsyncClient | None = None


async def init_supabase() -> None:
    global supabase
    supabase = await acreate_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
