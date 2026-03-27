import csv
import io
from datetime import datetime
from difflib import SequenceMatcher

from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.routers.admin_auth import require_admin
from app.models import Event, EventRegistration, Company, ContactPerson, AdminUser

router = APIRouter(prefix="/events", tags=["event_checkin"])
templates = Jinja2Templates(directory="app/templates")


# ---------------------------------------------------------------------------
# Fuzzy matching helpers
# ---------------------------------------------------------------------------

def fuzzy_ratio(a: str, b: str) -> float:
    """Return SequenceMatcher ratio for two strings (case-insensitive)."""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def find_best_company_match(name: str, companies: list[Company], threshold: float = 0.75):
    """Find the best matching company by name. Returns (company, ratio) or (None, 0)."""
    if not name:
        return None, 0.0
    best_company = None
    best_ratio = 0.0
    for company in companies:
        for candidate in [company.name, company.name2, company.name3]:
            if not candidate:
                continue
            ratio = fuzzy_ratio(name, candidate)
            if ratio > best_ratio:
                best_ratio = ratio
                best_company = company
    if best_ratio >= threshold:
        return best_company, best_ratio
    return None, best_ratio


def find_contact_person(
    email: str,
    first_name: str,
    last_name: str,
    db: Session,
    company_id: int | None = None,
) -> ContactPerson | None:
    """Try to match a contact person by email (exact) or name (fuzzy)."""
    # 1. Exact email match
    if email and not email.endswith("@placeholder.local"):
        cp = db.query(ContactPerson).filter(ContactPerson.email == email).first()
        if cp:
            return cp

    # 2. Fuzzy name match
    if first_name and last_name:
        query = db.query(ContactPerson)
        if company_id:
            query = query.filter(ContactPerson.company_id == company_id)
        candidates = query.all()
        for cp in candidates:
            name_ratio = fuzzy_ratio(
                f"{first_name} {last_name}",
                f"{cp.first_name} {cp.last_name}",
            )
            if name_ratio >= 0.80:
                return cp
    return None


def decode_csv_content(content: bytes) -> str:
    """Decode CSV bytes handling UTF-8, UTF-8-BOM, and Latin-1."""
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    return content.decode("latin-1")


# WP CSV column indices (0-based):
# 0=Company, 1=Appellation, 2=Title, 3=First Name, 4=Surname,
# 5=Position, 6=Email, 7=Phone, 8=Coming?,
# 9=Additional Company, 10=Additional Appellation, 11=Additional Title,
# 12=Additional First Name, 13=Additional Surname, 14=Additional Position,
# 15=Additional Email, 16=Additional Phone, 17=Info

WP_HEADER_FIELDS = [
    "company", "appellation", "title", "first_name", "last_name",
    "position", "email", "phone", "coming",
    "add_company", "add_appellation", "add_title", "add_first_name",
    "add_last_name", "add_position", "add_email", "add_phone", "info",
]


def parse_wp_row(values: list[str]) -> list[dict]:
    """Parse a WP CSV row into one or two person dicts."""
    # Pad to expected length
    while len(values) < len(WP_HEADER_FIELDS):
        values.append("")

    persons = []

    coming = values[8].strip()
    status = "angemeldet" if coming == "1" else "storniert"

    # Primary person
    primary = {
        "company": values[0].strip(),
        "appellation": values[1].strip(),
        "title": values[2].strip(),
        "first_name": values[3].strip(),
        "last_name": values[4].strip(),
        "position": values[5].strip(),
        "email": values[6].strip(),
        "phone": values[7].strip(),
        "status": status,
        "info": values[17].strip() if len(values) > 17 else "",
    }
    if primary["last_name"] or primary["email"]:
        persons.append(primary)

    # Additional person
    add_first = values[12].strip() if len(values) > 12 else ""
    add_last = values[13].strip() if len(values) > 13 else ""
    add_email = values[15].strip() if len(values) > 15 else ""
    if add_last or add_email:
        additional = {
            "company": (values[9].strip() if len(values) > 9 and values[9].strip() else primary["company"]),
            "appellation": values[10].strip() if len(values) > 10 else "",
            "title": values[11].strip() if len(values) > 11 else "",
            "first_name": add_first,
            "last_name": add_last,
            "position": values[14].strip() if len(values) > 14 else "",
            "email": add_email,
            "phone": values[16].strip() if len(values) > 16 else "",
            "status": status,
            "info": "",
        }
        persons.append(additional)

    return persons


# ---------------------------------------------------------------------------
# Wordpress CSV Upload & Fuzzy Matching
# ---------------------------------------------------------------------------

@router.get("/{event_id}/wp-import", response_class=HTMLResponse)
async def wp_import_form(
    request: Request,
    event_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return RedirectResponse(url="/events", status_code=303)

    return templates.TemplateResponse("events/wp_import.html", {
        "request": request,
        "event": event,
        "active_page": "events",
        "admin_user": admin.username,
    })


@router.post("/{event_id}/wp-import", response_class=HTMLResponse)
async def wp_import_upload(
    request: Request,
    event_id: int,
    csv_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return RedirectResponse(url="/events", status_code=303)

    content = await csv_file.read()
    text = decode_csv_content(content)

    # Strip Excel "sep=," hint line
    lines = text.strip().split("\n")
    if lines and lines[0].strip().lower().startswith("sep="):
        text = "\n".join(lines[1:])

    # Auto-detect delimiter: semicolon or comma
    first_line = text.strip().split("\n")[0] if text.strip() else ""
    if first_line.count(";") > first_line.count(","):
        delimiter = ";"
    else:
        delimiter = ","

    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    rows = list(reader)

    if not rows:
        return templates.TemplateResponse("events/wp_import.html", {
            "request": request,
            "event": event,
            "active_page": "events",
            "admin_user": admin.username,
            "flash_message": "Die CSV-Datei ist leer.",
            "flash_type": "warning",
        })

    # Skip header row
    data_rows = rows[1:] if len(rows) > 1 else rows

    # Load all companies for fuzzy matching
    all_companies = db.query(Company).filter(Company.is_active == True).all()

    matched = []      # Successfully matched
    unmatched = []     # Need manual review
    skipped = []       # Already exist

    for row_values in data_rows:
        persons = parse_wp_row(row_values)
        for person in persons:
            if not person.get("last_name") and not person.get("email"):
                continue

            # Check if already registered
            email = person["email"]
            existing = None
            if email:
                existing = (
                    db.query(EventRegistration)
                    .filter(
                        EventRegistration.event_id == event_id,
                        EventRegistration.email == email,
                    )
                    .first()
                )
            if not existing and person["first_name"] and person["last_name"]:
                # Check by name
                existing = (
                    db.query(EventRegistration)
                    .filter(
                        EventRegistration.event_id == event_id,
                        EventRegistration.first_name == person["first_name"],
                        EventRegistration.last_name == person["last_name"],
                    )
                    .first()
                )

            if existing:
                skipped.append({
                    "person": person,
                    "reason": "Bereits registriert",
                    "existing_id": existing.id,
                })
                continue

            # Fuzzy match company
            company_match, match_ratio = find_best_company_match(
                person["company"], all_companies
            )

            # Try to find contact person
            contact = find_contact_person(
                person["email"],
                person["first_name"],
                person["last_name"],
                db,
                company_id=company_match.id if company_match else None,
            )

            entry = {
                "person": person,
                "company_match": company_match,
                "match_ratio": match_ratio,
                "contact_person": contact,
            }

            if company_match:
                # Auto-create registration
                reg = EventRegistration(
                    event_id=event_id,
                    first_name=person["first_name"] or "Unbekannt",
                    last_name=person["last_name"] or "Unbekannt",
                    email=person["email"] or f"wp-import-{event_id}-{len(matched)}@placeholder.local",
                    phone=person["phone"] or None,
                    organization=person["company"],
                    status=person["status"],
                    company_id=company_match.id,
                    contact_person_id=contact.id if contact else None,
                    is_member=False,
                )
                db.add(reg)
                entry["imported"] = True
                matched.append(entry)
            else:
                entry["imported"] = False
                unmatched.append(entry)

    db.commit()

    return templates.TemplateResponse("events/wp_import.html", {
        "request": request,
        "event": event,
        "active_page": "events",
        "admin_user": admin.username,
        "matched": matched,
        "unmatched": unmatched,
        "skipped": skipped,
        "all_companies": all_companies,
        "show_results": True,
    })


@router.post("/{event_id}/wp-import/assign", response_class=HTMLResponse)
async def wp_import_assign(
    request: Request,
    event_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    """Manually assign unmatched WP import entries to companies and create registrations."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return RedirectResponse(url="/events", status_code=303)

    form = await request.form()
    imported_count = 0

    # Form fields follow pattern: first_name_0, last_name_0, email_0, company_id_0, ...
    idx = 0
    while True:
        first_name = form.get(f"first_name_{idx}")
        if first_name is None:
            break

        last_name = form.get(f"last_name_{idx}", "")
        email = form.get(f"email_{idx}", "")
        phone = form.get(f"phone_{idx}", "")
        organization = form.get(f"organization_{idx}", "")
        status = form.get(f"status_{idx}", "confirmed")
        company_id_str = form.get(f"company_id_{idx}", "")

        company_id = int(company_id_str) if company_id_str else None

        # Skip if no name
        if not last_name and not email:
            idx += 1
            continue

        # Check duplicate
        if email:
            existing = (
                db.query(EventRegistration)
                .filter(
                    EventRegistration.event_id == event_id,
                    EventRegistration.email == email,
                )
                .first()
            )
            if existing:
                idx += 1
                continue

        # Try to find contact person
        contact = find_contact_person(
            email, first_name, last_name, db,
            company_id=company_id,
        )

        reg = EventRegistration(
            event_id=event_id,
            first_name=first_name or "Unbekannt",
            last_name=last_name or "Unbekannt",
            email=email or f"wp-assign-{event_id}-{idx}@placeholder.local",
            phone=phone or None,
            organization=organization,
            status=status,
            company_id=company_id,
            contact_person_id=contact.id if contact else None,
            is_member=False,
        )
        db.add(reg)
        imported_count += 1
        idx += 1

    db.commit()

    return RedirectResponse(
        url=f"/events/{event_id}",
        status_code=303,
    )


# ---------------------------------------------------------------------------
# Check-In Mask
# ---------------------------------------------------------------------------

@router.get("/{event_id}/checkin", response_class=HTMLResponse)
async def checkin_page(
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

    # Only show confirmed registrations; sort: not-checked-in first, then checked-in
    registrations = [r for r in event.registrations if r.status == "confirmed"]
    registrations.sort(key=lambda r: (r.attendance == "attended", r.last_name.lower()))

    checked_in = sum(1 for r in registrations if r.attendance == "attended")

    return templates.TemplateResponse("events/checkin.html", {
        "request": request,
        "event": event,
        "registrations": registrations,
        "checked_in": checked_in,
        "total": len(registrations),
    })


@router.post("/{event_id}/checkin/{reg_id}", response_class=HTMLResponse)
async def checkin_person(
    request: Request,
    event_id: int,
    reg_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    """Mark a registration as attended (HTMX endpoint)."""
    reg = db.query(EventRegistration).filter(
        EventRegistration.id == reg_id,
        EventRegistration.event_id == event_id,
    ).first()

    if reg:
        reg.attendance = "attended"
        db.commit()
        db.refresh(reg)

    # Return updated card HTML for HTMX swap
    # Count totals for counter update
    all_confirmed = (
        db.query(EventRegistration)
        .filter(
            EventRegistration.event_id == event_id,
            EventRegistration.status == "confirmed",
        )
        .all()
    )
    checked_in = sum(1 for r in all_confirmed if r.attendance == "attended")
    total = len(all_confirmed)

    html = f"""
    <div class="checkin-card checked-in" id="reg-{reg.id}">
        <div class="checkin-card-info">
            <div class="checkin-name">{reg.first_name} {reg.last_name}</div>
            <div class="checkin-org">{reg.organization or ''}</div>
        </div>
        <div class="checkin-status">
            <i class="bi bi-check-circle-fill text-success" style="font-size: 2rem;"></i>
        </div>
    </div>
    <script>
        document.getElementById('checkin-counter').innerText = '{checked_in} / {total} eingecheckt';
    </script>
    """
    return HTMLResponse(content=html)


@router.post("/{event_id}/checkin/{reg_id}/undo", response_class=HTMLResponse)
async def undo_checkin(
    request: Request,
    event_id: int,
    reg_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    """Undo a check-in (HTMX endpoint)."""
    reg = db.query(EventRegistration).filter(
        EventRegistration.id == reg_id,
        EventRegistration.event_id == event_id,
    ).first()

    if reg:
        reg.attendance = None
        db.commit()
        db.refresh(reg)

    all_confirmed = (
        db.query(EventRegistration)
        .filter(
            EventRegistration.event_id == event_id,
            EventRegistration.status == "confirmed",
        )
        .all()
    )
    checked_in = sum(1 for r in all_confirmed if r.attendance == "attended")
    total = len(all_confirmed)

    html = f"""
    <div class="checkin-card" id="reg-{reg.id}">
        <div class="checkin-card-info">
            <div class="checkin-name">{reg.first_name} {reg.last_name}</div>
            <div class="checkin-org">{reg.organization or ''}</div>
        </div>
        <div class="checkin-action">
            <button class="btn btn-checkin"
                    hx-post="/events/{event_id}/checkin/{reg.id}"
                    hx-target="#reg-{reg.id}"
                    hx-swap="outerHTML">
                CHECK IN
            </button>
        </div>
    </div>
    <script>
        document.getElementById('checkin-counter').innerText = '{checked_in} / {total} eingecheckt';
    </script>
    """
    return HTMLResponse(content=html)


# ---------------------------------------------------------------------------
# Close Event (mark no-shows)
# ---------------------------------------------------------------------------

@router.post("/{event_id}/close", response_class=HTMLResponse)
async def close_event(
    event_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    """Mark all non-checked-in confirmed registrations as no_show."""
    regs = (
        db.query(EventRegistration)
        .filter(
            EventRegistration.event_id == event_id,
            EventRegistration.status == "confirmed",
            EventRegistration.attendance == None,  # noqa: E711
        )
        .all()
    )
    for reg in regs:
        reg.attendance = "no_show"
    db.commit()

    return RedirectResponse(url=f"/events/{event_id}", status_code=303)


# ---------------------------------------------------------------------------
# Manual Participant Addition
# ---------------------------------------------------------------------------

@router.post("/{event_id}/add-participant", response_class=HTMLResponse)
async def add_participant(
    request: Request,
    event_id: int,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(""),
    organization: str = Form(""),
    phone: str = Form(""),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    """Manually add a participant to an event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return RedirectResponse(url="/events", status_code=303)

    reg = EventRegistration(
        event_id=event_id,
        first_name=first_name,
        last_name=last_name,
        email=email or f"manual-{event_id}-{datetime.utcnow().timestamp():.0f}@placeholder.local",
        phone=phone or None,
        organization=organization or None,
        status="confirmed",
        is_member=False,
    )
    db.add(reg)
    db.commit()

    # Check if request came from checkin page (HTMX)
    if request.headers.get("HX-Request"):
        db.refresh(reg)
        all_confirmed = (
            db.query(EventRegistration)
            .filter(
                EventRegistration.event_id == event_id,
                EventRegistration.status == "confirmed",
            )
            .all()
        )
        checked_in = sum(1 for r in all_confirmed if r.attendance == "attended")
        total = len(all_confirmed)

        html = f"""
        <div class="checkin-card" id="reg-{reg.id}">
            <div class="checkin-card-info">
                <div class="checkin-name">{reg.first_name} {reg.last_name} <span class="badge bg-info">Walk-in</span></div>
                <div class="checkin-org">{reg.organization or ''}</div>
            </div>
            <div class="checkin-action">
                <button class="btn btn-checkin"
                        hx-post="/events/{event_id}/checkin/{reg.id}"
                        hx-target="#reg-{reg.id}"
                        hx-swap="outerHTML">
                    CHECK IN
                </button>
            </div>
        </div>
        <script>
            document.getElementById('checkin-counter').innerText = '{checked_in} / {total} eingecheckt';
            document.getElementById('walkin-modal').classList.remove('show');
            document.getElementById('walkin-modal').style.display = 'none';
            document.querySelector('.modal-backdrop')?.remove();
            document.body.classList.remove('modal-open');
            document.body.style = '';
        </script>
        """
        return HTMLResponse(content=html)

    return RedirectResponse(url=f"/events/{event_id}", status_code=303)
