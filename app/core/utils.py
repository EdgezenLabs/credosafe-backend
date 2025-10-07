import random
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta, timezone # <-- ADDED timezone
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.core.config import settings

def add_exception_handlers(app: FastAPI):
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        # NOTE: Keeping the generic handler, but be aware it masks the full traceback.
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "error": str(exc)}
        )

def generate_otp():
    return str(random.randint(100000, 999999))

# FIX: Use timezone.utc to make the datetime object timezone-aware
def get_expiry_time(minutes=5):
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)

def send_email_otp(recipient_email: str, otp_code: str):
    subject = "Your CredoSafe OTP Code"
    body = f"""
    Dear User,

    Your OTP for CredoSafe is: {otp_code}

    This code is valid for 5 minutes.

    Regards,
    CredoSafe Team
    """
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_SENDER_EMAIL
    msg["To"] = recipient_email

    try:
        with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"[Error] Failed to send OTP email: {e}")
