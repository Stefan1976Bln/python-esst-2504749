"""
Router fuer Veranstaltungs-Analyse, Score-Berechnung und Teilnahme-Nachpflege.
"""
from datetime import datetime

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.admin_auth import require_admin
from app.models import Event, EventRegistration, Company, AdminUser
from app.services.scoring import (
    compute_priority_score,
    score_all_registrations,
    get_event_analytics,
    get_person_event_history,
)

router = APIRouter(prefix="/events", tags=["analysis"])
templates = Jinja2Templates(directory="app/templates")


# ---------------------------------------------------------------------------
# Teilnahme nachpflegen (fuer vergangene Veranstaltungen)
# ---------------------------------------------------------------------------

@router.get("/{event_id}/attendance", response_class=HTMLResponse)
async def attendance_page(
    request: Request,
    event_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    """Page to manage attendance for a past event."""
    event = db.query(Event).get(event_id)
    if not event:
        return RedirectResponse(url="/events", status_code=303)

    regs = (
        db.query(EventRegistration)
        .filter(EventRegistration.event_id == event_id)
        .order_by(EventRegistration.last_name, EventRegistration.first_name)
        .all()
    )

    attended = sum(1 for r in regs if r.attendance == "attended")
    no_shows = sum(1 for r in regs if r.attendance == "no_show")
    untracked = sum(1 for r in regs if not r.attendance and r.status in ("zugelassen", "bestaetigt", "confirmed"))

    return templates.TemplateResponse("events/attendance.html", {
        "request": request,
        "event": event,
        "registrations": regs,
        "attended": attended,
        "no_shows": no_shows,
        "untracked": untracked,
        "active_page": "events",
        "admin_user": admin.username,
    })


@router.post("/{event_id}/attendance/{reg_id}", response_class=HTMLResponse)
async def set_attendance(
    event_id: int,
    reg_id: int,
    attendance: str = Form(...),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    """Set attendance for a single registration (HTMX)."""
    reg = db.query(EventRegistration).get(reg_id)
    if reg and reg.event_id == event_id:
        reg.attendance = attendance if attendance in ("attended", "no_show") else None
        if attendance == "attended" and not reg.checked_in_at:
            reg.checked_in_at = datetime.utcnow()
        db.commit()

    # Return updated row
    icon = _attendance_icon(reg.attendance if reg else None)
    name = reg.full_name if reg else ""
    org = reg.organization or ""
    return HTMLResponse(f"""
    <tr id="att-row-{reg_id}">
        <td>{name}</td>
        <td>{org}</td>
        <td>{reg.status_label if reg else ''}</td>
        <td class="text-center">{icon}</td>
        <td>
            <div class="btn-group btn-group-sm">
                <button class="btn btn-{'success' if reg and reg.attendance == 'attended' else 'outline-success'}"
                        hx-post="/events/{event_id}/attendance/{reg_id}"
                        hx-target="#att-row-{reg_id}" hx-swap="outerHTML"
                        hx-vals='{{"attendance": "attended"}}'>
                    <i class="bi bi-check-lg"></i> Teilgenommen
                </button>
                <button class="btn btn-{'danger' if reg and reg.attendance == 'no_show' else 'outline-danger'}"
                        hx-post="/events/{event_id}/attendance/{reg_id}"
                        hx-target="#att-row-{reg_id}" hx-swap="outerHTML"
                        hx-vals='{{"attendance": "no_show"}}'>
                    <i class="bi bi-x-lg"></i> No-Show
                </button>
                <button class="btn btn-outline-secondary"
                        hx-post="/events/{event_id}/attendance/{reg_id}"
                        hx-target="#att-row-{reg_id}" hx-swap="outerHTML"
                        hx-vals='{{"attendance": ""}}'>
                    <i class="bi bi-dash"></i>
                </button>
            </div>
        </td>
    </tr>
    """)


@router.post("/{event_id}/mark-all-noshow")
async def mark_all_noshow(
    event_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    """Mark all confirmed but untracked registrations as no-show."""
    regs = (
        db.query(EventRegistration)
        .filter(
            EventRegistration.event_id == event_id,
            EventRegistration.status.in_(["zugelassen", "bestaetigt", "confirmed"]),
            EventRegistration.attendance.is_(None),
        )
        .all()
    )
    for r in regs:
        r.attendance = "no_show"
    db.commit()
    return RedirectResponse(url=f"/events/{event_id}/attendance", status_code=303)


# ---------------------------------------------------------------------------
# Score-Berechnung & Rangfolge
# ---------------------------------------------------------------------------

@router.get("/{event_id}/scoring", response_class=HTMLResponse)
async def scoring_page(
    request: Request,
    event_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    """Show scoring / ranking page for an event."""
    event = db.query(Event).get(event_id)
    if not event:
        return RedirectResponse(url="/events", status_code=303)

    # Score all pending registrations
    ranked = score_all_registrations(db, event_id)

    # Already approved
    approved = (
        db.query(EventRegistration)
        .filter(
            EventRegistration.event_id == event_id,
            EventRegistration.status.in_(["zugelassen", "bestaetigt", "confirmed"]),
        )
        .order_by(EventRegistration.priority_score.desc().nullslast())
        .all()
    )

    return templates.TemplateResponse("events/scoring.html", {
        "request": request,
        "event": event,
        "ranked": ranked,
        "approved": approved,
        "active_page": "events",
        "admin_user": admin.username,
    })


@router.post("/{event_id}/approve/{reg_id}", response_class=HTMLResponse)
async def approve_registration(
    event_id: int,
    reg_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    """Approve a registration (change status to zugelassen)."""
    reg = db.query(EventRegistration).get(reg_id)
    if reg and reg.event_id == event_id:
        reg.status = "zugelassen"
        reg.confirmed_at = datetime.utcnow()
        db.commit()
    return HTMLResponse(f"""
    <tr class="table-success" id="score-row-{reg_id}">
        <td><strong>{reg.full_name if reg else ''}</strong></td>
        <td>{reg.organization or ''}</td>
        <td><span class="badge bg-success">Zugelassen</span></td>
        <td>{reg.priority_score or 0:.0f}/100</td>
        <td><span class="badge bg-success"><i class="bi bi-check-lg"></i> Zugelassen</span></td>
    </tr>
    """)


@router.post("/{event_id}/reject/{reg_id}", response_class=HTMLResponse)
async def reject_registration(
    event_id: int,
    reg_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    """Reject a registration."""
    reg = db.query(EventRegistration).get(reg_id)
    if reg and reg.event_id == event_id:
        reg.status = "abgelehnt"
        db.commit()
    return HTMLResponse(f"""
    <tr class="table-danger" id="score-row-{reg_id}">
        <td>{reg.full_name if reg else ''}</td>
        <td>{reg.organization or ''}</td>
        <td><span class="badge bg-danger">Abgelehnt</span></td>
        <td>{reg.priority_score or 0:.0f}/100</td>
        <td><span class="badge bg-danger"><i class="bi bi-x-lg"></i> Abgelehnt</span></td>
    </tr>
    """)


@router.post("/{event_id}/approve-top")
async def approve_top_n(
    event_id: int,
    count: int = Form(10),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    """Approve top N registrations by score."""
    regs = (
        db.query(EventRegistration)
        .filter(
            EventRegistration.event_id == event_id,
            EventRegistration.status.in_(["angemeldet", "pending"]),
        )
        .order_by(EventRegistration.priority_score.desc().nullslast())
        .limit(count)
        .all()
    )
    for r in regs:
        r.status = "zugelassen"
        r.confirmed_at = datetime.utcnow()
    db.commit()
    return RedirectResponse(url=f"/events/{event_id}/scoring", status_code=303)


# ---------------------------------------------------------------------------
# Veranstaltungs-Analyse
# ---------------------------------------------------------------------------

@router.get("/{event_id}/analysis", response_class=HTMLResponse)
async def analysis_page(
    request: Request,
    event_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    """Show analytics for an event."""
    analytics = get_event_analytics(db, event_id)
    if not analytics:
        return RedirectResponse(url="/events", status_code=303)

    return templates.TemplateResponse("events/analysis.html", {
        "request": request,
        "analytics": analytics,
        "event": analytics["event"],
        "active_page": "events",
        "admin_user": admin.username,
    })


# ---------------------------------------------------------------------------
# Score fuer einzelne Anmeldung anzeigen (HTMX)
# ---------------------------------------------------------------------------

@router.post("/{event_id}/score/{reg_id}", response_class=HTMLResponse)
async def show_score_detail(
    event_id: int,
    reg_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    """Compute and show detailed score for a registration."""
    result = compute_priority_score(db, reg_id)
    score = result["score"]

    # Score color
    if score >= 70:
        color = "success"
    elif score >= 40:
        color = "warning"
    else:
        color = "danger"

    reasons_html = "".join(f"<li>{r}</li>" for r in result["reasons"])
    parts = result.get("parts", {})

    parts_html = ""
    part_labels = {
        "zuverlaessigkeit": ("Zuverlaessigkeit", 30),
        "mitgliedschaft": ("Mitgliedsstatus", 25),
        "engagement": ("Engagement", 20),
        "fairness": ("Fairness/Wartezeit", 15),
        "diversitaet": ("Branchen-Diversitaet", 10),
    }
    for key, (label, max_val) in part_labels.items():
        val = parts.get(key, 0)
        pct = round(val / max_val * 100)
        parts_html += f"""
        <div class="mb-2">
            <div class="d-flex justify-content-between small">
                <span>{label}</span><span>{val}/{max_val}</span>
            </div>
            <div class="progress" style="height: 8px;">
                <div class="progress-bar bg-{color}" style="width: {pct}%"></div>
            </div>
        </div>
        """

    return HTMLResponse(f"""
    <div class="card border-0 shadow-sm">
        <div class="card-body">
            <div class="d-flex align-items-center mb-3">
                <div class="display-6 me-3 text-{color}"><strong>{score}</strong><small class="fs-6">/100</small></div>
                <div>
                    <p class="mb-0 small text-muted">{result['summary']}</p>
                </div>
            </div>
            {parts_html}
            <hr>
            <h6 class="small text-muted mb-2">Detailbegruendung:</h6>
            <ul class="small mb-0">{reasons_html}</ul>
        </div>
    </div>
    """)


def _attendance_icon(attendance: str | None) -> str:
    if attendance == "attended":
        return '<span class="badge bg-success"><i class="bi bi-check-circle-fill"></i> Teilgenommen</span>'
    elif attendance == "no_show":
        return '<span class="badge bg-danger"><i class="bi bi-x-circle-fill"></i> No-Show</span>'
    return '<span class="badge bg-secondary">Offen</span>'
