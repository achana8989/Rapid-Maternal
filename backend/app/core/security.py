import bcrypt
from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "super-secret-key-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def _truncate_bytes(text: str) -> bytes:
    if text is None:
        text = ""
    return text.encode("utf-8")[:72]


def hash_password(password: str) -> str:
    pw = _truncate_bytes(password)
    hashed = bcrypt.hashpw(pw, bcrypt.gensalt())
    return hashed.decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    pw = _truncate_bytes(plain_password)
    try:
        return bcrypt.checkpw(pw, hashed_password.encode())
    except ValueError:
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
