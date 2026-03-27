from datetime import datetime
from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.routers.admin_auth import require_admin
from app.models import Company, ContactPerson, Dossier, AdminUser

router = APIRouter(prefix="/companies", tags=["companies"])
templates = Jinja2Templates(directory="app/templates")


# ---------------------------------------------------------------------------
# Company list
# ---------------------------------------------------------------------------

@router.get("", response_class=HTMLResponse)
async def company_list(
    request: Request,
    q: str = Query("", alias="q"),
    branche: str = Query("", alias="branche"),
    status: str = Query("", alias="status"),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    query = db.query(Company)

    if q:
        search = f"%{q}%"
        query = query.filter(
            or_(
                Company.name.ilike(search),
                Company.city.ilike(search),
                Company.email.ilike(search),
            )
        )

    if branche:
        query = query.filter(Company.branche == branche)

    if status == "active":
        query = query.filter(Company.is_active == True)
    elif status == "inactive":
        query = query.filter(Company.is_active == False)

    companies = query.order_by(Company.name).all()

    # Collect distinct branches for the filter dropdown
    branches = (
        db.query(Company.branche)
        .filter(Company.branche.isnot(None), Company.branche != "")
        .distinct()
        .order_by(Company.branche)
        .all()
    )
    branches = [b[0] for b in branches]

    return templates.TemplateResponse(
        "companies/list.html",
        {
            "request": request,
            "companies": companies,
            "branches": branches,
            "q": q,
            "branche": branche,
            "status": status,
            "active_page": "companies",
            "admin_user": admin.username,
        },
    )


# ---------------------------------------------------------------------------
# Company create
# ---------------------------------------------------------------------------

@router.get("/new", response_class=HTMLResponse)
async def company_new(
    request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    return templates.TemplateResponse(
        "companies/form.html",
        {
            "request": request,
            "company": None,
            "active_page": "companies",
            "admin_user": admin.username,
        },
    )


@router.post("/new")
async def company_create(
    request: Request,
    name: str = Form(...),
    address: str = Form(""),
    postal_code: str = Form(""),
    city: str = Form(""),
    phone: str = Form(""),
    email: str = Form(""),
    website: str = Form(""),
    branche: str = Form(""),
    company_size: str = Form(""),
    membership_since: str = Form(""),
    is_active: bool = Form(True),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    company = Company(
        name=name,
        address=address or None,
        postal_code=postal_code or None,
        city=city or None,
        phone=phone or None,
        email=email or None,
        website=website or None,
        branche=branche or None,
        company_size=company_size or None,
        membership_since=datetime.strptime(membership_since, "%Y-%m-%d").date() if membership_since else None,
        is_active=is_active,
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return RedirectResponse(url=f"/companies/{company.id}", status_code=303)


# ---------------------------------------------------------------------------
# Company detail
# ---------------------------------------------------------------------------

@router.get("/{company_id}", response_class=HTMLResponse)
async def company_detail(
    request: Request,
    company_id: int,
    tab: str = Query("info", alias="tab"),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    company = (
        db.query(Company)
        .options(
            joinedload(Company.contacts),
            joinedload(Company.dossiers),
            joinedload(Company.fees),
        )
        .filter(Company.id == company_id)
        .first()
    )
    if not company:
        return RedirectResponse(url="/companies", status_code=303)

    return templates.TemplateResponse(
        "companies/detail.html",
        {
            "request": request,
            "company": company,
            "tab": tab,
            "active_page": "companies",
            "admin_user": admin.username,
        },
    )


# ---------------------------------------------------------------------------
# Company edit
# ---------------------------------------------------------------------------

@router.get("/{company_id}/edit", response_class=HTMLResponse)
async def company_edit(
    request: Request,
    company_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        return RedirectResponse(url="/companies", status_code=303)

    return templates.TemplateResponse(
        "companies/form.html",
        {
            "request": request,
            "company": company,
            "active_page": "companies",
            "admin_user": admin.username,
        },
    )


@router.post("/{company_id}/edit")
async def company_update(
    request: Request,
    company_id: int,
    name: str = Form(...),
    address: str = Form(""),
    postal_code: str = Form(""),
    city: str = Form(""),
    phone: str = Form(""),
    email: str = Form(""),
    website: str = Form(""),
    branche: str = Form(""),
    company_size: str = Form(""),
    membership_since: str = Form(""),
    is_active: bool = Form(False),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        return RedirectResponse(url="/companies", status_code=303)

    company.name = name
    company.address = address or None
    company.postal_code = postal_code or None
    company.city = city or None
    company.phone = phone or None
    company.email = email or None
    company.website = website or None
    company.branche = branche or None
    company.company_size = company_size or None
    company.membership_since = (
        datetime.strptime(membership_since, "%Y-%m-%d").date() if membership_since else None
    )
    company.is_active = is_active

    db.commit()
    return RedirectResponse(url=f"/companies/{company.id}", status_code=303)


# ---------------------------------------------------------------------------
# Company delete
# ---------------------------------------------------------------------------

@router.post("/{company_id}/delete")
async def company_delete(
    company_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    company = db.query(Company).filter(Company.id == company_id).first()
    if company:
        db.delete(company)
        db.commit()
    return RedirectResponse(url="/companies", status_code=303)


# ---------------------------------------------------------------------------
# Contacts  (HTMX partials)
# ---------------------------------------------------------------------------

@router.get("/{company_id}/contacts/new", response_class=HTMLResponse)
async def contact_new_form(
    request: Request,
    company_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    """Return an inline form for adding a new contact."""
    return HTMLResponse(f"""
    <tr id="contact-form-row">
      <form hx-post="/companies/{company_id}/contacts" hx-target="#contacts-table-body" hx-swap="innerHTML">
        <td><input type="text" name="first_name" class="form-control form-control-sm" placeholder="Vorname" required></td>
        <td><input type="text" name="last_name" class="form-control form-control-sm" placeholder="Nachname" required></td>
        <td><input type="text" name="role" class="form-control form-control-sm" placeholder="Funktion"></td>
        <td><input type="email" name="email" class="form-control form-control-sm" placeholder="E-Mail"></td>
        <td><input type="text" name="phone" class="form-control form-control-sm" placeholder="Telefon"></td>
        <td class="text-center"><input type="checkbox" name="is_primary" value="true" class="form-check-input"></td>
        <td>
          <button type="submit" class="btn btn-success btn-sm me-1"><i class="bi bi-check-lg"></i></button>
          <button type="button" class="btn btn-secondary btn-sm"
                  hx-get="/companies/{company_id}/contacts/list" hx-target="#contacts-table-body" hx-swap="innerHTML">
            <i class="bi bi-x-lg"></i>
          </button>
        </td>
      </form>
    </tr>
    """)


@router.get("/{company_id}/contacts/list", response_class=HTMLResponse)
async def contacts_list_partial(
    request: Request,
    company_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    """Return table rows for all contacts of a company."""
    contacts = (
        db.query(ContactPerson)
        .filter(ContactPerson.company_id == company_id)
        .order_by(ContactPerson.last_name)
        .all()
    )
    rows = ""
    for c in contacts:
        primary_badge = '<span class="badge bg-primary">Hauptkontakt</span>' if c.is_primary else ""
        rows += f"""
        <tr>
          <td>{c.first_name}</td>
          <td>{c.last_name}</td>
          <td>{c.role or ""} {primary_badge}</td>
          <td>{c.email or ""}</td>
          <td>{c.phone or ""}</td>
          <td class="text-center">{"<i class='bi bi-check-circle-fill text-success'></i>" if c.is_primary else ""}</td>
          <td>
            <button class="btn btn-outline-primary btn-sm me-1"
                    hx-get="/companies/{company_id}/contacts/{c.id}/edit"
                    hx-target="#contacts-table-body" hx-swap="innerHTML">
              <i class="bi bi-pencil"></i>
            </button>
            <button class="btn btn-outline-danger btn-sm"
                    hx-post="/companies/{company_id}/contacts/{c.id}/delete"
                    hx-target="#contacts-table-body" hx-swap="innerHTML"
                    hx-confirm="Ansprechpartner wirklich loeschen?">
              <i class="bi bi-trash"></i>
            </button>
          </td>
        </tr>
        """
    return HTMLResponse(rows)


@router.post("/{company_id}/contacts", response_class=HTMLResponse)
async def contact_create(
    request: Request,
    company_id: int,
    first_name: str = Form(...),
    last_name: str = Form(...),
    role: str = Form(""),
    email: str = Form(""),
    phone: str = Form(""),
    is_primary: bool = Form(False),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    contact = ContactPerson(
        company_id=company_id,
        first_name=first_name,
        last_name=last_name,
        role=role or None,
        email=email or None,
        phone=phone or None,
        is_primary=is_primary,
    )
    db.add(contact)
    db.commit()
    # Return updated list
    return await contacts_list_partial(request, company_id, db, admin)


@router.get("/{company_id}/contacts/{contact_id}/edit", response_class=HTMLResponse)
async def contact_edit_form(
    request: Request,
    company_id: int,
    contact_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    contact = db.query(ContactPerson).filter(ContactPerson.id == contact_id).first()
    if not contact:
        return await contacts_list_partial(request, company_id, db, admin)

    checked = "checked" if contact.is_primary else ""
    return HTMLResponse(f"""
    <tr id="contact-edit-row">
      <form hx-post="/companies/{company_id}/contacts/{contact_id}/edit" hx-target="#contacts-table-body" hx-swap="innerHTML">
        <td><input type="text" name="first_name" class="form-control form-control-sm" value="{contact.first_name}" required></td>
        <td><input type="text" name="last_name" class="form-control form-control-sm" value="{contact.last_name}" required></td>
        <td><input type="text" name="role" class="form-control form-control-sm" value="{contact.role or ''}"></td>
        <td><input type="email" name="email" class="form-control form-control-sm" value="{contact.email or ''}"></td>
        <td><input type="text" name="phone" class="form-control form-control-sm" value="{contact.phone or ''}"></td>
        <td class="text-center"><input type="checkbox" name="is_primary" value="true" class="form-check-input" {checked}></td>
        <td>
          <button type="submit" class="btn btn-success btn-sm me-1"><i class="bi bi-check-lg"></i></button>
          <button type="button" class="btn btn-secondary btn-sm"
                  hx-get="/companies/{company_id}/contacts/list" hx-target="#contacts-table-body" hx-swap="innerHTML">
            <i class="bi bi-x-lg"></i>
          </button>
        </td>
      </form>
    </tr>
    """)


@router.post("/{company_id}/contacts/{contact_id}/edit", response_class=HTMLResponse)
async def contact_update(
    request: Request,
    company_id: int,
    contact_id: int,
    first_name: str = Form(...),
    last_name: str = Form(...),
    role: str = Form(""),
    email: str = Form(""),
    phone: str = Form(""),
    is_primary: bool = Form(False),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    contact = db.query(ContactPerson).filter(ContactPerson.id == contact_id).first()
    if contact:
        contact.first_name = first_name
        contact.last_name = last_name
        contact.role = role or None
        contact.email = email or None
        contact.phone = phone or None
        contact.is_primary = is_primary
        db.commit()
    return await contacts_list_partial(request, company_id, db, admin)


@router.post("/{company_id}/contacts/{contact_id}/delete", response_class=HTMLResponse)
async def contact_delete(
    request: Request,
    company_id: int,
    contact_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    contact = db.query(ContactPerson).filter(ContactPerson.id == contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return await contacts_list_partial(request, company_id, db, admin)


# ---------------------------------------------------------------------------
# Dossiers  (HTMX partials)
# ---------------------------------------------------------------------------

@router.get("/{company_id}/dossiers/list", response_class=HTMLResponse)
async def dossiers_list_partial(
    request: Request,
    company_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    """Return the dossier timeline HTML."""
    dossiers = (
        db.query(Dossier)
        .filter(Dossier.entity_type == "company", Dossier.entity_id == company_id)
        .order_by(Dossier.created_at.desc())
        .all()
    )
    if not dossiers:
        return HTMLResponse('<p class="text-muted">Noch keine Eintraege vorhanden.</p>')

    html = ""
    for d in dossiers:
        date_str = d.created_at.strftime("%d.%m.%Y %H:%M") if d.created_at else ""
        html += f"""
        <div class="card mb-3">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start">
              <div>
                <h6 class="card-title mb-1">{d.title}</h6>
                <p class="card-text">{d.content}</p>
              </div>
              <button class="btn btn-outline-danger btn-sm ms-2"
                      hx-post="/companies/{company_id}/dossiers/{d.id}/delete"
                      hx-target="#dossier-timeline"
                      hx-swap="innerHTML"
                      hx-confirm="Eintrag wirklich loeschen?">
                <i class="bi bi-trash"></i>
              </button>
            </div>
            <small class="text-muted">
              <i class="bi bi-person me-1"></i>{d.author or "System"}
              <i class="bi bi-clock ms-2 me-1"></i>{date_str}
            </small>
          </div>
        </div>
        """
    return HTMLResponse(html)


@router.get("/{company_id}/dossiers/new", response_class=HTMLResponse)
async def dossier_new_form(
    request: Request,
    company_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    return HTMLResponse(f"""
    <div class="card mb-3" id="dossier-form">
      <div class="card-body">
        <form hx-post="/companies/{company_id}/dossiers" hx-target="#dossier-timeline" hx-swap="innerHTML">
          <div class="mb-3">
            <label class="form-label">Titel</label>
            <input type="text" name="title" class="form-control" placeholder="Betreff" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Inhalt</label>
            <textarea name="content" class="form-control" rows="3" placeholder="Notiz, Gespraechsprotokoll ..." required></textarea>
          </div>
          <button type="submit" class="btn btn-primary btn-sm me-1">
            <i class="bi bi-save me-1"></i>Speichern
          </button>
          <button type="button" class="btn btn-secondary btn-sm"
                  hx-get="/companies/{company_id}/dossiers/list"
                  hx-target="#dossier-timeline" hx-swap="innerHTML">
            Abbrechen
          </button>
        </form>
      </div>
    </div>
    """)


@router.post("/{company_id}/dossiers", response_class=HTMLResponse)
async def dossier_create(
    request: Request,
    company_id: int,
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    dossier = Dossier(
        entity_type="company",
        entity_id=company_id,
        title=title,
        content=content,
        author=admin.username,
    )
    db.add(dossier)
    db.commit()
    return await dossiers_list_partial(request, company_id, db, admin)


@router.post("/{company_id}/dossiers/{dossier_id}/delete", response_class=HTMLResponse)
async def dossier_delete(
    request: Request,
    company_id: int,
    dossier_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    dossier = db.query(Dossier).filter(Dossier.id == dossier_id).first()
    if dossier:
        db.delete(dossier)
        db.commit()
    return await dossiers_list_partial(request, company_id, db, admin)
