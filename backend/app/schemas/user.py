from pydantic import BaseModel, EmailStr
from typing import Optional

# =========================
# USER CREATION (ADMIN)
# =========================
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str  # admin, midwife, nurse, doctor
    facility_id: Optional[int] = None


# =========================
# USER RESPONSE
# =========================
class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    facility_id: Optional[int]

    class Config:
        from_attributes = True  # ✅ Pydantic v2 compatible


# =========================
# LOGIN REQUEST (AUTH)
# =========================
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
