from typing import Optional
from pydantic import BaseModel

class TelegramOidcCallback(BaseModel):
    code: str
    code_verifier: str

class SessionResponse(BaseModel):
    session_token: str
    user: dict
    # Dikirim terpisah dari `user` (bukan cuma field di dalamnya) supaya
    # frontend bisa langsung pakai tanpa harus tahu bentuk objek user.
    role: str = "producer"
