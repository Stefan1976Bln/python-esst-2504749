import csv
import io
import re
from datetime import datetime

from fastapi import APIRouter, Request, Depends, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.admin_auth import require_admin
from app.models import Company, ContactPerson
from app.models.user import AdminUser

router = APIRouter(prefix="/import", tags=["import"])
templates = Jinja2Templates(directory="app/templates")


def _parse_date(value: str):
    """Parse a DD.MM.YYYY date string. Returns None on empty/invalid input."""
    if not value or not value.strip():
        return None
    value = value.strip()
    try:
        return datetime.strptime(value, "%d.%m.%Y").date()
    except ValueError:
        return None


def _parse_float(value: str):
    """Parse a float from a German-style string (e.g. '1.200,50' or '50,00').
    Strips non-numeric chars except comma and dot, then normalises."""
    if not value or not value.strip():
        return None
    value = value.strip()
    # Remove everything except digits, comma, dot, minus
    cleaned = re.sub(r"[^\d,.\-]", "", value)
    if not cleaned:
        return None
    # German format: dots as thousands separators, comma as decimal
    cleaned = cleaned.replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_int(value: str):
    """Parse an integer from string. Returns None on empty/invalid."""
    if not value or not value.strip():
        return None
    try:
        return int(value.strip())
    except ValueError:
        return None


def _decode_contents(raw: bytes) -> str:
    """Try UTF-8 first, fall back to Latin-1."""
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def _strip(val: str | None) -> str | None:
    """Return stripped value or None if empty."""
    if val is None:
        return None
    val = val.strip()
    return val if val else None


# ---------------------------------------------------------------------------
# GET /import  -  Upload form
# ---------------------------------------------------------------------------

@router.get("", response_class=HTMLResponse)
async def import_page(
    request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    return templates.TemplateResponse(
        "companies/import.html",
        {
            "request": request,
            "active_page": "companies",
            "admin_user": admin.username,
            "results": None,
        },
    )


# ---------------------------------------------------------------------------
# POST /import/companies  -  Process CSV upload
# ---------------------------------------------------------------------------

@router.post("/companies", response_class=HTMLResponse)
async def import_companies(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    results = {
        "companies_created": 0,
        "companies_updated": 0,
        "contacts_added": 0,
        "errors": [],
        "warnings": [],
    }

    # Read and decode file
    raw = await file.read()
    if not raw:
        results["errors"].append("Die hochgeladene Datei ist leer.")
        return _render(request, admin, results)

    text = _decode_contents(raw)
    reader = csv.DictReader(io.StringIO(text), delimiter=";")

    # Validate header
    if reader.fieldnames is None:
        results["errors"].append("CSV-Header konnte nicht gelesen werden.")
        return _render(request, admin, results)

    # Track which companies already received their first contact in this import
    # key = company.id  ->  True if at least one contact was added
    companies_with_contact: dict[int, bool] = {}

    for row_num, row in enumerate(reader, start=2):
        try:
            _process_row(row, row_num, db, results, companies_with_contact)
        except Exception as exc:
            results["errors"].append(f"Zeile {row_num}: Unerwarteter Fehler - {exc}")

    db.commit()
    return _render(request, admin, results)


def _render(request: Request, admin: AdminUser, results: dict):
    return templates.TemplateResponse(
        "companies/import.html",
        {
            "request": request,
            "active_page": "companies",
            "admin_user": admin.username,
            "results": results,
        },
    )


def _process_row(
    row: dict,
    row_num: int,
    db: Session,
    results: dict,
    companies_with_contact: dict[int, bool],
):
    """Process a single CSV row: find/create company, then create contact."""
    firma = _strip(row.get("Firma"))
    vorname = _strip(row.get("Vorname")) or ""
    nachname = _strip(row.get("Name")) or ""

    if not vorname and not nachname and not firma:
        results["warnings"].append(f"Zeile {row_num}: Leerzeile uebersprungen.")
        return

    crm_id = _parse_int(row.get("ID"))

    # ---- Determine / create company ----------------------------------------
    company = None
    is_new_company = False

    if firma:
        # Try to find by CRM ID first
        if crm_id:
            company = db.query(Company).filter(Company.crm_id == crm_id).first()
        # Fall back to name match
        if not company:
            company = db.query(Company).filter(Company.name == firma).first()

        if company:
            results["companies_updated"] += 1
        else:
            is_new_company = True
            company = Company(name=firma, is_active=True)
            db.add(company)
    else:
        # Private person - always create a new company record
        private_name = f"Privatperson: {vorname} {nachname}".strip()
        is_new_company = True
        company = Company(name=private_name, is_active=True)
        db.add(company)

    # ---- Update company fields (from first occurrence or always overwrite) --
    if is_new_company or True:
        # Always update company address/meta from CSV (last row wins)
        company.name2 = _strip(row.get("Firma2")) or company.name2
        company.name3 = _strip(row.get("Firma3")) or company.name3
        company.address = _strip(row.get("ZustellStrasse")) or company.address
        company.postal_code = _strip(row.get("ZustellPLZ")) or company.postal_code
        company.city = _strip(row.get("ZustellOrt")) or company.city
        company.staat = _strip(row.get("Staat")) or company.staat
        company.branche = _strip(row.get("Branche")) or company.branche
        company.frei1 = _strip(row.get("Frei 1")) or company.frei1
        company.rechnungstext = _strip(row.get("Rechnungstext")) or company.rechnungstext

        beitrag = _parse_float(row.get("Beitrag ?"))
        if beitrag is not None:
            company.beitrag = beitrag

        membership_since = _parse_date(row.get("Eintrittsdatum"))
        if membership_since:
            company.membership_since = membership_since

        membership_end = _parse_date(row.get("Austrittsdatum-Ort"))
        if membership_end:
            company.membership_end = membership_end

        if crm_id is not None:
            company.crm_id = crm_id

    if is_new_company:
        results["companies_created"] += 1
        # Flush so the company gets an ID
        db.flush()

    # ---- Create contact person ----------------------------------------------
    if not vorname and not nachname:
        results["warnings"].append(
            f"Zeile {row_num}: Kein Ansprechpartner (Vorname/Nachname leer) - "
            f"nur Firmendaten importiert."
        )
        return

    # Determine if this contact should be primary
    is_primary = company.id not in companies_with_contact
    companies_with_contact[company.id] = True

    contact = ContactPerson(
        company_id=company.id,
        anrede=_strip(row.get("AnPerson")),
        titel=_strip(row.get("Titel")),
        first_name=vorname,
        last_name=nachname,
        position=_strip(row.get("Position")),
        abteilung=_strip(row.get("Abteilung")),
        phone=_strip(row.get("Telefon")),
        phone_direct=_strip(row.get("Direkt")),
        phone_mobile=_strip(row.get("Mobil")),
        phone_private=_strip(row.get("Privat")),
        email=_strip(row.get("E-Mail")),
        birthday=_parse_date(row.get("Geburtstag")),
        is_primary=is_primary,
        crm_id=crm_id,
    )
    db.add(contact)
    results["contacts_added"] += 1


# ---------------------------------------------------------------------------
# GET /import/preview  -  Future: preview before import
# ---------------------------------------------------------------------------

@router.get("/preview", response_class=HTMLResponse)
async def import_preview(
    request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    return HTMLResponse("<p>Vorschau-Funktion wird in einer zukuenftigen Version verfuegbar sein.</p>")
