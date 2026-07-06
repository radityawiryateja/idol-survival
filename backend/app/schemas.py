from typing import Optional
from pydantic import BaseModel

class TelegramOidcCallback(BaseModel):
    code: str
    code_verifier: str

class SessionResponse(BaseModel):
    session_token: str
    user: dict
