import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    SESSION_SECRET: str = os.getenv("SESSION_SECRET", "change-me")
    SESSION_EXPIRE_MINUTES: int = int(os.getenv("SESSION_EXPIRE_MINUTES", "10080"))
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    TELEGRAM_OIDC_CLIENT_ID: str = os.getenv("TELEGRAM_OIDC_CLIENT_ID", "")
    TELEGRAM_OIDC_CLIENT_SECRET: str = os.getenv("TELEGRAM_OIDC_CLIENT_SECRET", "")
    TELEGRAM_OIDC_REDIRECT_URI: str = os.getenv("TELEGRAM_OIDC_REDIRECT_URI", "")


settings = Settings()
