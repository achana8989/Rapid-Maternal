from app.db.database import SessionLocal, engine
from app.db.models import User

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def seed_users():
    db = SessionLocal()

    users = [
        {
            "username": "admin",
            "full_name": "System Admin",
            "role": "admin",
            "password": "admin123",
        },
        {
            "username": "midwife1",
            "full_name": "Midwife One",
            "role": "midwife",
            "password": "midwife123",
        },
    ]

    for u in users:
        exists = db.query(User).filter(User.username == u["username"]).first()
        if exists:
            print(f"User {u['username']} already exists — skipping")
            continue

        user = User(
            username=u["username"],
            full_name=u["full_name"],
            role=u["role"],
            hashed_password=hash_password(u["password"]),
        )
        db.add(user)

    db.commit()
    db.close()
    print("✅ Users seeded successfully")

if __name__ == "__main__":
    seed_users()
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])  # bcrypt hard limit
