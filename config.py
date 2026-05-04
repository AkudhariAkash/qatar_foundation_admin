import os
from datetime import timedelta
from urllib.parse import quote_plus
from dotenv import load_dotenv


# Load .env only for local development. On Render, use dashboard env vars.
if not os.getenv("RENDER"):
    load_dotenv()


def _build_database_uri():
    explicit_uri = os.getenv("DATABASE_URL")
    if explicit_uri:
        # Render commonly provides postgres://... which SQLAlchemy doesn't accept directly.
        if explicit_uri.startswith("postgres://"):
            explicit_uri = explicit_uri.replace("postgres://", "postgresql+psycopg2://", 1)
        return explicit_uri

    if os.getenv("RENDER"):
        raise RuntimeError("DATABASE_URL is required on Render. Set it in Render Environment Variables.")

    db_host = os.getenv("DB_HOST")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "qf_admin")

    if db_host and db_user and db_password:
        safe_user = quote_plus(db_user)
        safe_password = quote_plus(db_password)
        return f"postgresql+psycopg2://{safe_user}:{safe_password}@{db_host}:{db_port}/{db_name}"

    return "sqlite:///qf_admin.db"


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = _build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REMEMBER_COOKIE_DURATION = timedelta(days=14)
    RESET_TOKEN_MAX_AGE_SECONDS = 3600
    ALLOWED_CATEGORIES = {
        "Technology",
        "Business",
        "Design",
        "Marketing",
        "Healthcare",
        "Education",
        "Finance",
        "Other",
    }
