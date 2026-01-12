from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.core.security import SECRET_KEY, ALGORITHM

# Define the OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    return payload


def require_role(allowed_roles: list):
    def role_checker(current: dict = Depends(get_current_user)):
        role = current.get("role")
        if role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Access denied")

        return current
    return role_checker
