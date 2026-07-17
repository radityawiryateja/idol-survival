import hashlib
import hmac
import time
from urllib.parse import parse_qsl

from app.config import settings

MAX_AUTH_AGE_SECONDS = 24 * 60 * 60


def verify_telegram_auth(data: dict) -> bool:
    if not settings.TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")

    received_hash = data.get("hash")
    if not received_hash:
        return False

    check_fields = {k: v for k, v in data.items() if k != "hash" and v is not None}
    data_check_string = "\n".join(f"{k}={check_fields[k]}" for k in sorted(check_fields))

    secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
    computed_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        return False

    auth_date = int(data.get("auth_date", 0))
    if time.time() - auth_date > MAX_AUTH_AGE_SECONDS:
        return False

    return True

def verify_webapp_init_data(init_data: str) -> dict | None:
    """
    Validasi data yang dikirimkan oleh Telegram Web App (Mini App).
    """
    if not settings.TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")

    # Parse query string init_data menjadi dictionary
    parsed_data = dict(parse_qsl(init_data))
    if "hash" not in parsed_data:
        return None

    received_hash = parsed_data.pop("hash")
    
    # Format string sesuai abjad
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed_data.items()))

    # Secret key untuk Web App menggunakan HMAC SHA256 dari "WebAppData" dan bot token
    secret_key = hmac.new(
        b"WebAppData", settings.TELEGRAM_BOT_TOKEN.encode(), hashlib.sha256
    ).digest()

    computed_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        return None
        
    auth_date = int(parsed_data.get("auth_date", 0))
    if time.time() - auth_date > MAX_AUTH_AGE_SECONDS:
        return None

    return parsed_data
