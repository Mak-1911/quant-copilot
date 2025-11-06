from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
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

def send_email_otp(to_email: str, otp_code: str):
    msg = EmailMessage()
    msg["Subject"] = "Your Quant-Copilot OTP Code"
    msg["From"] = SMTP_USER
    msg["To"] = to_email

    # Plain-text fallback
    text_body = (
        "Greetings from Quant-Copilot!\n\n"
        f"Your OTP code is: {otp_code}\n"
        "This code is valid for 15 minutes.\n\n"
        "If you did not request this, you can ignore this email."
    )
    msg.set_content(text_body)

    # HTML version
    html_body = f"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="color-scheme" content="light dark">
    <meta name="supported-color-schemes" content="light dark">
    <style>
      :root {{
        color-scheme: light dark;
        supported-color-schemes: light dark;
      }}
      body {{
        margin: 0; padding: 0; background: #0b1020; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
      }}
      .wrapper {{
        width: 100%; background: #0b1020; padding: 32px 0;
      }}
      .card {{
        max-width: 560px; margin: 0 auto; background: #12172b; border: 1px solid #1e2644; border-radius: 12px; overflow: hidden;
      }}
      .header {{
        padding: 20px 24px; background: linear-gradient(135deg, #243b55 0%, #141e30 100%);
        color: #fff; font-weight: 600; font-size: 16px;
      }}
      .content {{
        padding: 24px; color: #e6e8f2; line-height: 1.6;
      }}
      .otp {{
        display: inline-block; margin: 12px 0 16px; padding: 14px 20px; font-size: 28px; letter-spacing: 6px; 
        font-weight: 700; color: #fff; background: #1f2b4a; border: 1px solid #2c3b68; border-radius: 10px;
      }}
      .btn {{
        display: inline-block; padding: 12px 18px; background: #3b82f6; color: #fff !important; text-decoration: none; 
        border-radius: 8px; font-weight: 600; margin-top: 6px;
      }}
      .meta {{
        margin-top: 18px; font-size: 12px; color: #aab1d0;
      }}
      .footer {{
        text-align: center; padding: 18px; font-size: 12px; color: #8d95b8;
      }}
      @media (prefers-color-scheme: light) {{
        body {{ background: #f4f6fb; }}
        .wrapper {{ background: #f4f6fb; }}
        .card {{ background: #ffffff; border-color: #e7eaf3; }}
        .header {{ background: linear-gradient(135deg, #2563eb 0%, #1e3a8a 100%); }}
        .content {{ color: #1f2937; }}
        .otp {{ background: #f3f4f6; color: #111827; border-color: #e5e7eb; }}
        .meta {{ color: #6b7280; }}
        .footer {{ color: #6b7280; }}
      }}
    </style>
  </head>
  <body>
    <div class="wrapper">
      <div class="card">
        <div class="header">Quant-Copilot • One-Time Passcode</div>
        <div class="content">
          <p>Hello,</p>
          <p>Use the OTP below to continue your sign-in. This code expires in 15 minutes.</p>
          <div class="otp">{otp_code}</div>
          <p>
            If you didn’t request this code, you can safely ignore this email.
          </p>
          <p class="meta">
            This is an automated message; replies aren’t monitored.
          </p>
        </div>
        <div class="footer">
          © {datetime.utcnow().year} Quant-Copilot
        </div>
      </div>
    </div>
  </body>
</html>
"""
    msg.add_alternative(html_body, subtype="html")

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


