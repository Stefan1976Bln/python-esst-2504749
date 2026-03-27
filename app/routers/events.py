import os
import uuid
from datetime import datetime

import aiofiles
from PIL import Image
from fastapi import APIRouter, Request, Depends, Form, Query, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.config import settings
from app.routers.admin_auth import require_admin
from app.models import Event, EventImage, EventRegistration, AdminUser

router = APIRouter(prefix="/events", tags=["events"])
templates = Jinja2Templates(directory="app/templates")

EVENT_TYPES = ["City-Talk", "Stammtisch", "KTS Fruehstueck", "Workshop", "Networking", "Seminar", "Gala", "Konferenz", "Messe"]

MAX_IMAGE_SIZE = (1920, 1080)
THUMB_SIZE = (400, 300)


# ---------------------------------------------------------------------------
# Helper: save uploaded image
# ---------------------------------------------------------------------------

async def save_event_image(
    upload: UploadFile, event_id: int, db: Session
) -> EventImage:
    """Save an uploaded image, resize it, and create a DB record."""
    event_dir = os.path.join(settings.UPLOAD_DIR, "events", str(event_id))
    os.makedirs(event_dir, exist_ok=True)

    ext = os.path.splitext(upload.filename or "image.jpg")[1].lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
        ext = ".jpg"

    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(event_dir, filename)

    content = await upload.read()
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(content)

    # Resize with Pillow
    try:
        img = Image.open(filepath)
        img.thumbnail(MAX_IMAGE_SIZE, Image.LANCZOS)
        img.save(filepath, quality=85)
    except Exception:
        pass  # keep original if resize fails

    relative_path = f"/data/uploads/events/{event_id}/{filename}"

    # Check if this is the first image (make it primary)
    existing_count = db.query(EventImage).filter(EventImage.event_id == event_id).count()

    image = EventImage(
        event_id=event_id,
        file_path=relative_path,
        is_primary=existing_count == 0,
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


# ---------------------------------------------------------------------------
# Event list
# ---------------------------------------------------------------------------

@router.get("", response_class=HTMLResponse)
async def event_list(
    request: Request,
    q: str = Query("", alias="q"),
    event_type: str = Query("", alias="event_type"),
    status: str = Query("", alias="status"),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    query = db.query(Event)

    if q:
        search = f"%{q}%"
        query = query.filter(
            or_(
                Event.title.ilike(search),
                Event.location.ilike(search),
                Event.description.ilike(search),
            )
        )

    if event_type:
        query = query.filter(Event.event_type == event_type)

    if status == "upcoming":
        query = query.filter(Event.event_date >= datetime.utcnow())
    elif status == "past":
        query = query.filter(Event.event_date < datetime.utcnow())
    elif status == "published":
        query = query.filter(Event.is_published == True)
    elif status == "draft":
        query = query.filter(Event.is_published == False)

    events = (
        query.options(joinedload(Event.registrations))
        .order_by(Event.event_date.desc())
        .all()
    )

    return templates.TemplateResponse(
        "events/list.html",
        {
            "request": request,
            "events": events,
            "event_types": EVENT_TYPES,
            "q": q,
            "event_type": event_type,
            "status": status,
            "active_page": "events",
            "admin_user": admin.username,
        },
    )


# ---------------------------------------------------------------------------
# Event create
# ---------------------------------------------------------------------------

@router.get("/new", response_class=HTMLResponse)
async def event_create_form(
    request: Request,
    admin: AdminUser = Depends(require_admin),
):
    return templates.TemplateResponse(
        "events/form.html",
        {
            "request": request,
            "event": None,
            "event_types": EVENT_TYPES,
            "active_page": "events",
            "admin_user": admin.username,
        },
    )


@router.post("/new", response_class=HTMLResponse)
async def event_create(
    request: Request,
    title: str = Form(...),
    event_type: str = Form(""),
    description: str = Form(""),
    location: str = Form(""),
    address: str = Form(""),
    event_date: str = Form(...),
    event_end_date: str = Form(""),
    max_participants: str = Form(""),
    registration_deadline: str = Form(""),
    registration_url: str = Form(""),
    is_published: bool = Form(False),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    event = Event(
        title=title,
        event_type=event_type or None,
        description=description or None,
        location=location or None,
        address=address or None,
        event_date=datetime.fromisoformat(event_date),
        event_end_date=datetime.fromisoformat(event_end_date) if event_end_date else None,
        max_participants=int(max_participants) if max_participants else None,
        registration_deadline=datetime.fromisoformat(registration_deadline) if registration_deadline else None,
        registration_url=registration_url or None,
        is_published=is_published,
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    return RedirectResponse(url=f"/events/{event.id}", status_code=303)


# ---------------------------------------------------------------------------
# Event detail
# ---------------------------------------------------------------------------

@router.get("/{event_id}", response_class=HTMLResponse)
async def event_detail(
    request: Request,
    event_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    event = (
        db.query(Event)
        .options(joinedload(Event.images), joinedload(Event.registrations))
        .filter(Event.id == event_id)
        .first()
    )
    if not event:
        return RedirectResponse(url="/events", status_code=303)

    public_url = f"{settings.BASE_URL}/public/events/{event.public_token}"

    return templates.TemplateResponse(
        "events/detail.html",
        {
            "request": request,
            "event": event,
            "public_url": public_url,
            "active_page": "events",
            "admin_user": admin.username,
        },
    )


# ---------------------------------------------------------------------------
# Event edit
# ---------------------------------------------------------------------------

@router.get("/{event_id}/edit", response_class=HTMLResponse)
async def event_edit_form(
    request: Request,
    event_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return RedirectResponse(url="/events", status_code=303)

    return templates.TemplateResponse(
        "events/form.html",
        {
            "request": request,
            "event": event,
            "event_types": EVENT_TYPES,
            "active_page": "events",
            "admin_user": admin.username,
        },
    )


@router.post("/{event_id}/edit", response_class=HTMLResponse)
async def event_edit(
    request: Request,
    event_id: int,
    title: str = Form(...),
    event_type: str = Form(""),
    description: str = Form(""),
    location: str = Form(""),
    address: str = Form(""),
    event_date: str = Form(...),
    event_end_date: str = Form(""),
    max_participants: str = Form(""),
    registration_deadline: str = Form(""),
    is_published: bool = Form(False),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return RedirectResponse(url="/events", status_code=303)

    event.title = title
    event.event_type = event_type or None
    event.description = description or None
    event.location = location or None
    event.address = address or None
    event.event_date = datetime.fromisoformat(event_date)
    event.event_end_date = datetime.fromisoformat(event_end_date) if event_end_date else None
    event.max_participants = int(max_participants) if max_participants else None
    event.registration_deadline = datetime.fromisoformat(registration_deadline) if registration_deadline else None
    event.registration_url = registration_url or None
    event.is_published = is_published

    db.commit()
    return RedirectResponse(url=f"/events/{event.id}", status_code=303)


# ---------------------------------------------------------------------------
# Event delete
# ---------------------------------------------------------------------------

@router.post("/{event_id}/delete", response_class=HTMLResponse)
async def event_delete(
    event_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if event:
        db.delete(event)
        db.commit()
    return RedirectResponse(url="/events", status_code=303)


# ---------------------------------------------------------------------------
# Image upload
# ---------------------------------------------------------------------------

@router.post("/{event_id}/images", response_class=HTMLResponse)
async def upload_image(
    request: Request,
    event_id: int,
    image: UploadFile = File(...),
    caption: str = Form(""),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return RedirectResponse(url="/events", status_code=303)

    img_record = await save_event_image(image, event_id, db)
    if caption:
        img_record.caption = caption
        db.commit()

    return RedirectResponse(url=f"/events/{event_id}", status_code=303)


@router.post("/{event_id}/images/{image_id}/delete", response_class=HTMLResponse)
async def delete_image(
    event_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    img = db.query(EventImage).filter(
        EventImage.id == image_id, EventImage.event_id == event_id
    ).first()
    if img:
        # Try to delete file from disk
        try:
            full_path = os.path.join(settings.UPLOAD_DIR, "events", str(event_id), os.path.basename(img.file_path))
            if os.path.exists(full_path):
                os.remove(full_path)
        except Exception:
            pass
        db.delete(img)
        db.commit()
    return RedirectResponse(url=f"/events/{event_id}", status_code=303)


@router.post("/{event_id}/images/{image_id}/primary", response_class=HTMLResponse)
async def set_primary_image(
    event_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    # Reset all images for this event
    db.query(EventImage).filter(EventImage.event_id == event_id).update({"is_primary": False})
    # Set selected as primary
    img = db.query(EventImage).filter(
        EventImage.id == image_id, EventImage.event_id == event_id
    ).first()
    if img:
        img.is_primary = True
        db.commit()
    return RedirectResponse(url=f"/events/{event_id}", status_code=303)


# ---------------------------------------------------------------------------
# Registration management (HTMX)
# ---------------------------------------------------------------------------

@router.post("/{event_id}/registrations/{reg_id}/approve", response_class=HTMLResponse)
async def approve_registration(
    request: Request,
    event_id: int,
    reg_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    reg = db.query(EventRegistration).filter(
        EventRegistration.id == reg_id, EventRegistration.event_id == event_id
    ).first()
    if reg:
        reg.status = "confirmed"
        reg.confirmed_at = datetime.utcnow()
        db.commit()
        db.refresh(reg)

    return templates.TemplateResponse(
        "events/_registration_row.html",
        {"request": request, "reg": reg, "event": reg.event},
    )


@router.post("/{event_id}/registrations/{reg_id}/reject", response_class=HTMLResponse)
async def reject_registration(
    request: Request,
    event_id: int,
    reg_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    reg = db.query(EventRegistration).filter(
        EventRegistration.id == reg_id, EventRegistration.event_id == event_id
    ).first()
    if reg:
        reg.status = "rejected"
        db.commit()
        db.refresh(reg)

    return templates.TemplateResponse(
        "events/_registration_row.html",
        {"request": request, "reg": reg, "event": reg.event},
    )


@router.post("/{event_id}/registrations/{reg_id}/waitlist", response_class=HTMLResponse)
async def waitlist_registration(
    request: Request,
    event_id: int,
    reg_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    reg = db.query(EventRegistration).filter(
        EventRegistration.id == reg_id, EventRegistration.event_id == event_id
    ).first()
    if reg:
        reg.status = "waitlisted"
        db.commit()
        db.refresh(reg)

    return templates.TemplateResponse(
        "events/_registration_row.html",
        {"request": request, "reg": reg, "event": reg.event},
    )


@router.post("/{event_id}/registrations/{reg_id}/attendance", response_class=HTMLResponse)
async def set_attendance(
    request: Request,
    event_id: int,
    reg_id: int,
    attendance: str = Form(...),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    reg = db.query(EventRegistration).filter(
        EventRegistration.id == reg_id, EventRegistration.event_id == event_id
    ).first()
    if reg:
        reg.attendance = attendance if attendance else None
        db.commit()
        db.refresh(reg)

    return templates.TemplateResponse(
        "events/_registration_row.html",
        {"request": request, "reg": reg, "event": reg.event},
    )


# ---------------------------------------------------------------------------
# AI summary generation (placeholder)
# ---------------------------------------------------------------------------

@router.post("/{event_id}/generate-summary", response_class=HTMLResponse)
async def generate_ai_summary(
    request: Request,
    event_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    event = (
        db.query(Event)
        .options(joinedload(Event.registrations))
        .filter(Event.id == event_id)
        .first()
    )
    if not event:
        return RedirectResponse(url="/events", status_code=303)

    # Build a summary from registration data
    total = len(event.registrations)
    confirmed = event.confirmed_count
    attended = sum(1 for r in event.registrations if r.attendance == "attended")
    no_show = sum(1 for r in event.registrations if r.attendance == "no_show")
    orgs = set(r.organization for r in event.registrations if r.organization)

    summary_parts = [
        f"Veranstaltung: {event.title} ({event.event_type or 'Allgemein'})",
        f"Datum: {event.event_date.strftime('%d.%m.%Y %H:%M')}",
        f"Ort: {event.location or 'Nicht angegeben'}",
        f"Anmeldungen gesamt: {total}, Bestaetigt: {confirmed}",
        f"Teilgenommen: {attended}, Nicht erschienen: {no_show}",
        f"Beteiligte Organisationen: {', '.join(sorted(orgs)) if orgs else 'Keine'}",
    ]

    event.ai_summary = "\n".join(summary_parts)
    db.commit()

    return RedirectResponse(url=f"/events/{event_id}", status_code=303)


# ---------------------------------------------------------------------------
# Publish / Unpublish toggle
# ---------------------------------------------------------------------------

@router.post("/{event_id}/toggle-publish", response_class=HTMLResponse)
async def toggle_publish(
    event_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if event:
        event.is_published = not event.is_published
        db.commit()
    return RedirectResponse(url=f"/events/{event_id}", status_code=303)


# ---------------------------------------------------------------------------
# CSV Upload for participant lists
# ---------------------------------------------------------------------------

@router.get("/{event_id}/csv-upload", response_class=HTMLResponse)
async def csv_upload_form(
    request: Request,
    event_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return RedirectResponse(url="/events", status_code=303)
    return templates.TemplateResponse("events/csv_upload.html", {
        "request": request,
        "event": event,
        "active_page": "events",
        "admin_user": admin.username,
    })


@router.post("/{event_id}/csv-upload", response_class=HTMLResponse)
async def csv_upload(
    request: Request,
    event_id: int,
    csv_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    import csv
    import io

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return RedirectResponse(url="/events", status_code=303)

    content = await csv_file.read()
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    fieldnames = reader.fieldnames or []
    if len(fieldnames) <= 1:
        reader = csv.DictReader(io.StringIO(text), delimiter=",")
        fieldnames = reader.fieldnames or []

    imported = 0

    header_map = {
        "vorname": "first_name", "first_name": "first_name", "firstname": "first_name",
        "nachname": "last_name", "last_name": "last_name", "lastname": "last_name", "name": "last_name",
        "e-mail": "email", "email": "email", "mail": "email",
        "telefon": "phone", "phone": "phone", "tel": "phone",
        "unternehmen": "organization", "firma": "organization", "organisation": "organization",
        "organization": "organization", "company": "organization",
        "branche": "branche", "industry": "branche",
        "status": "attendance", "teilnahme": "attendance", "attendance": "attendance",
    }

    normalized_fields = {}
    for f in fieldnames:
        key = f.strip().lower().replace("\u00e4", "ae").replace("\u00f6", "oe").replace("\u00fc", "ue")
        if key in header_map:
            normalized_fields[f] = header_map[key]

    for i, row in enumerate(reader, start=2):
        mapped = {}
        for orig_col, target_col in normalized_fields.items():
            mapped[target_col] = (row.get(orig_col) or "").strip()

        first_name = mapped.get("first_name", "")
        last_name = mapped.get("last_name", "")
        email = mapped.get("email", "")

        if not last_name and not email:
            continue

        if not first_name:
            parts = last_name.split(" ", 1)
            if len(parts) == 2:
                first_name, last_name = parts

        if not email:
            email = f"import-{event_id}-{i}@placeholder.local"

        existing = (
            db.query(EventRegistration)
            .filter(EventRegistration.event_id == event_id, EventRegistration.email == email)
            .first()
        )
        if existing:
            attendance = mapped.get("attendance", "").lower()
            if attendance in ("ja", "yes", "attended", "teilgenommen", "1"):
                existing.attendance = "attended"
            elif attendance in ("nein", "no", "no_show", "nicht erschienen", "0"):
                existing.attendance = "no_show"
            db.commit()
            continue

        reg = EventRegistration(
            event_id=event_id,
            first_name=first_name or "Unbekannt",
            last_name=last_name or "Unbekannt",
            email=email,
            phone=mapped.get("phone"),
            organization=mapped.get("organization"),
            branche=mapped.get("branche"),
            is_member=False,
            status="confirmed",
        )

        attendance = mapped.get("attendance", "").lower()
        if attendance in ("ja", "yes", "attended", "teilgenommen", "1"):
            reg.attendance = "attended"
        elif attendance in ("nein", "no", "no_show", "nicht erschienen", "0"):
            reg.attendance = "no_show"

        db.add(reg)
        imported += 1

    db.commit()

    return templates.TemplateResponse("events/csv_upload.html", {
        "request": request,
        "event": event,
        "active_page": "events",
        "admin_user": admin.username,
        "flash_message": f"{imported} Teilnehmer erfolgreich importiert.",
        "flash_type": "success",
        "imported": imported,
    })
