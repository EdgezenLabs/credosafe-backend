import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change_me")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    OTP_EXPIRY_MINUTES: int = int(os.getenv("OTP_EXPIRY_MINUTES", "5"))
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.zoho.in")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 465))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "sunil.jas@edgezenlabs.com")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "India143#")
    SMTP_SENDER_EMAIL: str = os.getenv("SMTP_SENDER_EMAIL", "sunil.jas@edgezenlabs.com")

settings = Settings()
