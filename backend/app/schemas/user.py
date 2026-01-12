from pydantic import BaseModel, EmailStr
from typing import Optional

# =========================
# USER CREATION (ADMIN)
# =========================
class UserCreate(BaseModel):
    full_name: str
    username: str
    email: Optional[EmailStr] = None  # optional
    password: str
    role: str  # admin, midwife, nurse, doctor
    facility_id: Optional[int] = None
    facility_name: Optional[str] = None


# =========================
# USER RESPONSE
# =========================
class UserOut(BaseModel):
    id: int
    full_name: Optional[str] = None
    username: str
    email: Optional[EmailStr] = None
    role: str
    facility_id: Optional[int]
    facility_name: Optional[str] = None

    class Config:
        from_attributes = True  # ✅ Pydantic v2 compatible


# =========================
# LOGIN REQUEST (AUTH)
# =========================
class LoginRequest(BaseModel):
    username: str
    password: str