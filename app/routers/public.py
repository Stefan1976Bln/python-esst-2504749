from datetime import datetime

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Event, EventRegistration
from app.services.email import send_email, registration_confirmation_html

router = APIRouter(prefix="/p", tags=["public"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/events")
async def public_event_list(request: Request, db: Session = Depends(get_db)):
    """Public listing of upcoming published events. URL: /p/events"""
    events = (
        db.query(Event)
        .filter(Event.is_published == True, Event.event_date >= datetime.utcnow())
        .order_by(Event.event_date.asc())
        .all()
    )
    return templates.TemplateResponse("public/event_list.html", {
        "request": request,
        "events": events,
    })


@router.get("/e/{token}")
async def public_event_register_form(request: Request, token: str, db: Session = Depends(get_db)):
    """Show event details and registration form."""
    event = db.query(Event).filter(Event.public_token == token).first()
    if not event:
        return templates.TemplateResponse("public/register.html", {
            "request": request,
            "event": None,
            "error": "Veranstaltung nicht gefunden.",
        })

    # Check deadline
    deadline_passed = False
    if event.registration_deadline and event.registration_deadline < datetime.utcnow():
        deadline_passed = True

    # Check capacity
    full = False
    if event.max_participants:
        confirmed = sum(1 for r in event.registrations if r.status in ("confirmed", "pending"))
        if confirmed >= event.max_participants:
            full = True

    return templates.TemplateResponse("public/register.html", {
        "request": request,
        "event": event,
        "deadline_passed": deadline_passed,
        "full": full,
    })


@router.post("/e/{token}/register")
async def public_event_register(
    request: Request,
    token: str,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(""),
    organization: str = Form(""),
    branche: str = Form(""),
    is_member: bool = Form(False),
    motivation: str = Form(""),
    db: Session = Depends(get_db),
):
    """Process public registration."""
    event = db.query(Event).filter(Event.public_token == token).first()
    if not event:
        return templates.TemplateResponse("public/register.html", {
            "request": request,
            "event": None,
            "error": "Veranstaltung nicht gefunden.",
        })

    # Create registration
    registration = EventRegistration(
        event_id=event.id,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone or None,
        organization=organization or None,
        branche=branche or None,
        is_member=is_member,
        motivation=motivation or None,
        status="pending",
    )
    db.add(registration)
    db.commit()
    db.refresh(registration)

    # Send confirmation email
    event_date_str = event.event_date.strftime("%d.%m.%Y %H:%M")
    html_body = registration_confirmation_html(
        name=f"{first_name} {last_name}",
        event_title=event.title,
        event_date=event_date_str,
    )
    await send_email(
        db=db,
        to_email=email,
        subject=f"Anmeldebestaetigung: {event.title}",
        html_body=html_body,
        template_name="registration_confirmation",
    )

    return templates.TemplateResponse("public/confirmation.html", {
        "request": request,
        "event": event,
        "registration": registration,
    })
