from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.dependencies import require_role
from app.core.security import hash_password

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# Only admin roles can register new users
@router.post("/register", response_model=UserOut)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["facility_admin", "district_admin"]))
):
    # Check if email already exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_pw = hash_password(user_data.password)

    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        password_hash=hashed_pw,
        role=user_data.role,
        facility_id=user_data.facility_id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
