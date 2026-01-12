from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from app.dependencies import require_role
from passlib.hash import bcrypt
from app.schemas.user import UserCreate, UserOut

# Define the router
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/register", response_model=UserOut)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["facility_admin", "district_admin"]))
):
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_pw = bcrypt.hash(user_data.password)

    new_user = User(
        username=user_data.username,
        password=hashed_pw,
        role=user_data.role,
        facility_id=getattr(user_data, "facility_id", None)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
