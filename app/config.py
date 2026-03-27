import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Defaults are set for local development (no Docker)
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'agcity.db')}")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    CLAUDE_API_KEY: str = os.getenv("CLAUDE_API_KEY", "")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM: str = os.getenv("SMTP_FROM", "noreply@agcity.example.com")
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8500")
    ADMIN_DEFAULT_PASSWORD: str = os.getenv("ADMIN_DEFAULT_PASSWORD", "admin123")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "uploads"))
    PORT: int = int(os.getenv("PORT", "8500"))


settings = Settings()
