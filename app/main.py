import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from passlib.hash import bcrypt

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models import *  # noqa: F401, F403 - ensure all models registered
from app.models.user import AdminUser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    """Create all tables and seed default admin user."""
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if not admin:
            admin = AdminUser(
                username="admin",
                password_hash=bcrypt.hash(settings.ADMIN_DEFAULT_PASSWORD),
                full_name="Administrator",
                is_active=True,
            )
            db.add(admin)
            db.commit()
            logger.info("Default admin user created (admin / %s)", settings.ADMIN_DEFAULT_PASSWORD)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    init_db()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "events"), exist_ok=True)
    logger.info("AG City application started")
    yield
    logger.info("AG City application shutting down")


app = FastAPI(title="AG City Verwaltung", lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
from app.routers.admin_auth import router as auth_router, RedirectException  # noqa: E402
from app.routers.companies import router as companies_router  # noqa: E402
from app.routers.events import router as events_router  # noqa: E402
from app.routers.dashboard import router as dashboard_router  # noqa: E402
from app.routers.public import router as public_router  # noqa: E402
from app.routers.fees import router as fees_router  # noqa: E402
from app.routers.ai_api import router as ai_router  # noqa: E402
from app.routers.csv_import import router as import_router  # noqa: E402
from app.routers.event_checkin import router as checkin_router  # noqa: E402
from app.routers.event_analysis import router as analysis_router  # noqa: E402

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(companies_router)
app.include_router(checkin_router)
app.include_router(events_router)
app.include_router(public_router)
app.include_router(fees_router)
app.include_router(ai_router)
app.include_router(import_router)
app.include_router(analysis_router)


@app.exception_handler(RedirectException)
async def redirect_to_login(request: Request, exc: RedirectException):
    return RedirectResponse(url="/auth/login", status_code=303)


@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard")
