from typing import Optional
from pydantic import BaseModel


class TelegramAuthPayload(BaseModel):
    """Shape of the object the Telegram Login Widget passes to onauth()."""
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str


class SessionResponse(BaseModel):
    session_token: str
    user: dict
