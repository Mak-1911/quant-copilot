from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from jose import jwt
import os, random, smtplib
from email.message import EmailMessage
from app.utility.redis_client import redis_client
from app.db import get_session
from sqlmodel import select
from app.models.users import User

router = APIRouter(prefix="/auth")

JWT_SECRET = os.getenv("JWT_SECRET","quantcopilotsecret")
JWT_EXPIRY_DATES = 15

SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

def send_email_otp(to_email:str, otp_code:str):
    msg = EmailMessage()
    msg["Subject"] = "Quant-Copilot OTP Code"
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg.set_content(f"Greetings from Quant-Copilot! \n Your OTP code is: {otp_code} \n This code is valid for 15 minutes.")
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(SMTP_USER, SMTP_PASS)
        smtp.send_message(msg)

@router.post("/request-otp")
def request_otp(email: str):
    otp = str(random.randint(100000, 999999))
    redis_client.setex(f"otp:{email}", timedelta(minutes=10), otp)
    send_email_otp(email, otp)
    return {"message": "OTP sent to your email."}

@router.post("/verify-otp")
def verify_otp(email:str, otp_code:str):
    stored_otp = redis_client.get(f"otp:{email}")
    if not stored_otp or stored_otp != otp_code:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")
    
    redis_client.delete(f"otp:{email}") #Clear OTP after verification
    with get_session() as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if not user:
            user = User(email=email)
            session.add(user)
            session.commit()
            session.refresh(user)

    token = jwt.encode(
        {"sub":user.email, "exp": datetime.utcnow()+timedelta(days=JWT_EXPIRY_DATES)},
        JWT_SECRET, algorithm="HS256"
    )
    return {"access_token": token, "token_type": "bearer"}