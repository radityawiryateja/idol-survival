"""Role-based access control helpers.

Dipakai di atas `get_current_user` (app/routers/protected.py) yang sudah
memvalidasi session JWT. Modul ini cuma menambahkan lapisan cek role di
atasnya, jadi endpoint yang sudah ada tidak perlu diubah kalau tidak butuh
proteksi role.
"""

from fastapi import Depends, HTTPException

from app.routers.protected import get_current_user

VALID_ROLES = {"producer", "idol", "admin"}


def require_role(*roles: str):
    """Factory dependency: `Depends(require_role("admin"))`,
    `Depends(require_role("admin", "idol"))`, dst.
    """
    allowed = set(roles) or VALID_ROLES

    async def _dependency(current_user: dict = Depends(get_current_user)) -> dict:
        role = current_user.get("role", "producer")
        if role not in allowed:
            raise HTTPException(
                status_code=403,
                detail="Kamu tidak punya akses ke resource ini",
            )
        return current_user

    return _dependency
