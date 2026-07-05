"""
Validates the payload sent by the Telegram Login Widget.

Telegram's spec: https://core.telegram.org/widgets/login
1. Remove the "hash" field from the payload.
2. Build a data-check-string: all remaining fields as "key=value",
   sorted alphabetically by key, joined with "\n".
3. secret_key = SHA256(bot_token)
4. computed_hash = HMAC-SHA256(data_check_string, secret_key), hex-encoded
5. computed_hash must equal the "hash" field the widget sent.
6. auth_date should not be too old (replay-attack mitigation).
"""
import hashlib
import hmac
import time

from app.config import settings

MAX_AUTH_AGE_SECONDS = 24 * 60 * 60  # 1 day


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
