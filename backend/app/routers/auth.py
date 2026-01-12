from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, get_db
from app.db.models import User
from app.db.models import Facility
from app.schemas.user import LoginRequest, UserCreate, UserOut
from app.core.security import hash_password, verify_password, create_access_token
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])


# Create default users at startup (simple seeding)
def create_default_users():
    db = SessionLocal()
    if not db.query(User).filter(User.username == "admin").first():
        admin_user = User(
            username="admin",
            password=hash_password("admin123"),
            role="ADMIN"
        )
        db.add(admin_user)
    if not db.query(User).filter(User.username == "midwife1").first():
        midwife_user = User(
            username="midwife1",
            password=hash_password("password123"),
            role="MIDWIFE",
            facility_id=1
        )
        db.add(midwife_user)
    if not db.query(User).filter(User.username == "subadmin").first():
        sub_user = User(
            username="subadmin",
            password=hash_password("subpass123"),
            role="SUBDISTRICT_ADMIN"
        )
        db.add(sub_user)
    db.commit()
    db.close()


create_default_users()


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.username == data.username).first()

        if not user or not verify_password(data.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        token_data = {
            "sub": user.username,
            "role": user.role,
            "facility_id": user.facility_id,
        }

        token = create_access_token(token_data)
        return {"access_token": token}
    except HTTPException:
        raise
    except Exception as e:
        # log and surface the error for debugging during development
        print("[auth.login] internal error:", repr(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register/midwife", response_model=UserOut)
def register_midwife(payload: UserCreate, db: Session = Depends(get_db)):
    # enforce role to be MIDWIFE for this endpoint
    role = (payload.role or "MIDWIFE").upper()
    if role != "MIDWIFE":
        role = "MIDWIFE"

    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Resolve facility by name if provided, or require facility_id/name
    facility_id = getattr(payload, "facility_id", None)
    facility_name = getattr(payload, "facility_name", None)

    if not facility_id and not facility_name:
        raise HTTPException(status_code=400, detail="facility_id or facility_name is required for midwife registration")

    if facility_name and not facility_id:
        # find or create facility
        f = db.query(Facility).filter(Facility.name.ilike(facility_name)).first()
        if not f:
            f = Facility(name=facility_name)
            db.add(f)
            db.commit()
            db.refresh(f)
        facility_id = f.id

    hashed = hash_password(payload.password)
    new_user = User(
        username=payload.username,
        password=hashed,
        role=role,
        full_name=getattr(payload, "full_name", None),
        email=getattr(payload, "email", None),
        facility_id=facility_id,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
