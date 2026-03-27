from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from itsdangerous import URLSafeSerializer

from app.database import get_db
from app.config import settings
from app.models.user import AdminUser

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

serializer = URLSafeSerializer(settings.SECRET_KEY)


def get_current_admin(request: Request, db: Session = Depends(get_db)) -> AdminUser | None:
    """Dependency: get current admin from session cookie."""
    token = request.cookies.get("session")
    if not token:
        return None
    try:
        user_id = serializer.loads(token)
        return db.query(AdminUser).filter(AdminUser.id == user_id, AdminUser.is_active == True).first()
    except Exception:
        return None


def require_admin(request: Request, db: Session = Depends(get_db)) -> AdminUser:
    """Dependency: require admin login, redirect if not authenticated."""
    admin = get_current_admin(request, db)
    if not admin:
        raise RedirectException()
    return admin


class RedirectException(Exception):
    pass


@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not user or not bcrypt.verify(password, user.password_hash):
        return templates.TemplateResponse("auth/login.html", {"request": request, "error": "Ungueltige Anmeldedaten"})

    token = serializer.dumps(user.id)
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie("session", token, httponly=True, samesite="lax", max_age=86400 * 7)
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("session")
    return response
