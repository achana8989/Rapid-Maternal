# create_users.py

from app.db.database import SessionLocal
from app.db.models import User
from app.core.security import hash_password, verify_password


def create_user(db, username, password, role):
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        print(f"⚠️ {username} already exists")
        return

    user = User(
        username=username,
        password=hash_password(password),
        role=role
    )
    db.add(user)
    db.commit()
    print(f"✅ Created {username}")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        create_user(db, "admin", "admin123", "facility_admin")
        create_user(db, "midwife1", "password123", "midwife")
    finally:
        db.close()
