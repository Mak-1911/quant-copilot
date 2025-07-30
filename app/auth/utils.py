from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import os
from app.models.users import User
from app.db import get_session
from sqlmodel import select

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/verify-otp")
JWT_SECRET = os.getenv("JWT_SECRET", "quantcopilotsecret")

def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        email =  payload.get("sub")
        with get_session() as session:
            user = session.exec(select(User).where(User.email == email)).first()
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            return user.email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")