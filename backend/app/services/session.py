"""Issues and verifies the session tokens returned to the frontend after login."""
import datetime
from typing import Optional

import jwt

from app.config import settings

ALGORITHM = "HS256"


def create_session_token(user_id: str, telegram_id: int, role: str = "producer") -> str:
    now = datetime.datetime.utcnow()
    payload = {
        "sub": user_id,
        "telegram_id": telegram_id,
        # Klaim role dipakai oleh app/services/rbac.py untuk proteksi rute
        # per-role (producer / idol / admin). Default 'producer' supaya
        # token lama (yang di-decode ulang tanpa klaim ini) tetap jalan.
        "role": role,
        "iat": now,
        "exp": now + datetime.timedelta(minutes=settings.SESSION_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.SESSION_SECRET, algorithm=ALGORITHM)


def decode_session_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SESSION_SECRET, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None
