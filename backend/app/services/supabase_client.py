from supabase import Client, create_client

from app.config import settings

# Uses the service-role key because this client runs on the backend only.
# Never ship the service-role key to the frontend.
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
