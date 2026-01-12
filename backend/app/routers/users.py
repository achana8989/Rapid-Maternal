from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.db.models import User, Facility
from app.dependencies import require_role
from app.schemas.user import UserCreate, UserOut
from app.core.security import hash_password

# Define the router
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/register", response_model=UserOut)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["SUBDISTRICT_ADMIN", "ADMIN"]))
):
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")

    # resolve facility by id or name (create if needed)
    facility_id = getattr(user_data, 'facility_id', None)
    if not facility_id and getattr(user_data, 'facility_name', None):
        name = user_data.facility_name.strip()
        facility = db.query(Facility).filter(func.lower(Facility.name) == name.lower()).first()
        if not facility:
            facility = Facility(name=name)
            db.add(facility)
            db.commit()
            db.refresh(facility)
        facility_id = facility.id

    hashed_pw = hash_password(user_data.password)

    new_user = User(
        username=user_data.username,
        password=hashed_pw,
        role=(user_data.role or '').upper(),
        full_name=getattr(user_data, 'full_name', None),
        email=getattr(user_data, 'email', None),
        facility_id=facility_id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), current_user = Depends(require_role(["SUBDISTRICT_ADMIN", "ADMIN"]))):
    users = db.query(User).order_by(User.created_at.desc()).all()
    results = []
    for u in users:
        facility = None
        if u.facility_id:
            facility = db.query(Facility).filter(Facility.id == u.facility_id).first()
        results.append({
            "id": u.id,
            "full_name": getattr(u, 'full_name', None),
            "username": u.username,
            "email": getattr(u, 'email', None),
            "role": u.role,
            "facility_id": u.facility_id,
            "facility_name": facility.name if facility else None,
        })
    return results


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user = Depends(require_role(["SUBDISTRICT_ADMIN", "ADMIN"]))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Only allow deletion of midwife accounts via this endpoint
    if (user.role or '').upper() != 'MIDWIFE':
        raise HTTPException(status_code=403, detail="Can only remove midwife accounts")

    db.delete(user)
    db.commit()
    return {"detail": "deleted"}
