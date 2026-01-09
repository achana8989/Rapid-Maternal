from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from app.core.security import SECRET_KEY, ALGORITHM

# Define the OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def require_role(allowed_roles: list):
    def role_checker(token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

        role = payload.get("role")
        if role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Access denied")

        return payload
    return role_checker
