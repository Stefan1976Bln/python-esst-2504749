from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.admin_auth import require_admin
from app.models import Company, Event, EventRegistration
from app.services import ai_analysis

router = APIRouter(prefix="/ai", tags=["ai"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/insights")
async def insights_page(request: Request, admin=Depends(require_admin), db: Session = Depends(get_db)):
    """Main AI insights page."""
    companies = db.query(Company).filter(Company.is_active == True).order_by(Company.name).all()
    events = db.query(Event).order_by(Event.event_date.desc()).limit(20).all()
    recent_registrations = (
        db.query(EventRegistration)
        .order_by(EventRegistration.registered_at.desc())
        .limit(20)
        .all()
    )
    return templates.TemplateResponse("ai/insights.html", {
        "request": request,
        "companies": companies,
        "events": events,
        "recent_registrations": recent_registrations,
        "active_page": "ai",
        "admin_user": admin.username,
    })


@router.post("/reliability/{email}")
async def compute_reliability(email: str, admin=Depends(require_admin), db: Session = Depends(get_db)):
    """Compute reliability score for an email address."""
    if not email:
        return HTMLResponse('<div class="alert alert-warning">Bitte E-Mail angeben.</div>')
    result = await ai_analysis.compute_reliability_score(db, email)
    score = result["score"]
    color = _score_color(score)
    return HTMLResponse(f"""
    <div class="card border-0 shadow-sm">
        <div class="card-body">
            <h6 class="mb-2"><i class="bi bi-shield-check me-1"></i> Zuverlaessigkeits-Score fuer {email}</h6>
            <div class="d-flex align-items-center mb-2">
                <div class="progress flex-grow-1 me-3" style="height: 20px;">
                    <div class="progress-bar bg-{color}" style="width: {score*100:.0f}%">{score:.2f}</div>
                </div>
                <span class="badge bg-{color} fs-6">{score:.2f}</span>
            </div>
            <p class="text-muted small mb-0">{result["reasoning"]}</p>
        </div>
    </div>
    """)


@router.post("/suitability/{registration_id}")
async def compute_suitability(registration_id: int, admin=Depends(require_admin),
                              db: Session = Depends(get_db)):
    """Compute suitability score for a registration."""
    result = await ai_analysis.compute_suitability_score(db, registration_id)
    score = result["score"]
    reasoning = result.get("reasoning", "")
    recommendation = result.get("recommendation", "waitlist")
    color = _score_color(score)

    rec_badges = {
        "approve": '<span class="badge bg-success">Empfehlung: Zusagen</span>',
        "reject": '<span class="badge bg-danger">Empfehlung: Absagen</span>',
        "waitlist": '<span class="badge bg-warning text-dark">Empfehlung: Warteliste</span>',
    }
    rec_badge = rec_badges.get(recommendation, f'<span class="badge bg-secondary">{recommendation}</span>')

    return HTMLResponse(f"""
    <div class="card border-0 shadow-sm">
        <div class="card-body">
            <h6 class="mb-2"><i class="bi bi-person-check me-1"></i> Passungs-Score</h6>
            <div class="d-flex align-items-center mb-2">
                <div class="progress flex-grow-1 me-3" style="height: 20px;">
                    <div class="progress-bar bg-{color}" style="width: {score*100:.0f}%">{score:.2f}</div>
                </div>
                <span class="badge bg-{color} fs-6">{score:.2f}</span>
            </div>
            <div class="mb-2">{rec_badge}</div>
            <p class="text-muted small mb-0">{reasoning}</p>
        </div>
    </div>
    """)


@router.post("/engagement/{company_id}")
async def compute_engagement(company_id: int, admin=Depends(require_admin), db: Session = Depends(get_db)):
    """Compute engagement score for a company."""
    result = await ai_analysis.compute_engagement_score(db, company_id)
    company = db.query(Company).get(company_id)
    score = result.get("score", 0)
    reasoning = result.get("reasoning", "")
    recommendations = result.get("recommendations", [])
    color = _score_color(score)

    recs_html = ""
    if recommendations:
        recs_html = '<ul class="small text-muted mb-0 mt-2">'
        for r in recommendations:
            recs_html += f"<li>{r}</li>"
        recs_html += "</ul>"

    return HTMLResponse(f"""
    <div class="card border-0 shadow-sm">
        <div class="card-body">
            <h6 class="mb-2"><i class="bi bi-graph-up me-1"></i> Engagement: {company.name if company else 'Unbekannt'}</h6>
            <div class="d-flex align-items-center mb-2">
                <div class="progress flex-grow-1 me-3" style="height: 20px;">
                    <div class="progress-bar bg-{color}" style="width: {score*100:.0f}%">{score:.2f}</div>
                </div>
                <span class="badge bg-{color} fs-6">{score:.2f}</span>
            </div>
            <p class="text-muted small mb-0">{reasoning}</p>
            {recs_html}
        </div>
    </div>
    """)


@router.post("/churn/{company_id}")
async def compute_churn(company_id: int, admin=Depends(require_admin), db: Session = Depends(get_db)):
    """Compute churn risk for a company."""
    result = await ai_analysis.compute_churn_risk(db, company_id)
    company = db.query(Company).get(company_id)
    score = result.get("score", 0)
    reasoning = result.get("reasoning", "")
    warnings = result.get("warning_signs", [])
    actions = result.get("retention_actions", [])
    # For churn: high score = bad (red), low score = good (green)
    color = _score_color_inverted(score)

    warnings_html = ""
    if warnings:
        warnings_html = '<div class="mt-2"><strong class="small">Warnsignale:</strong><ul class="small text-muted mb-0">'
        for w in warnings:
            warnings_html += f'<li class="text-danger">{w}</li>'
        warnings_html += "</ul></div>"

    actions_html = ""
    if actions:
        actions_html = '<div class="mt-2"><strong class="small">Massnahmen:</strong><ul class="small text-muted mb-0">'
        for a in actions:
            actions_html += f'<li class="text-success">{a}</li>'
        actions_html += "</ul></div>"

    return HTMLResponse(f"""
    <div class="card border-0 shadow-sm">
        <div class="card-body">
            <h6 class="mb-2"><i class="bi bi-exclamation-triangle me-1"></i> Churn-Risiko: {company.name if company else 'Unbekannt'}</h6>
            <div class="d-flex align-items-center mb-2">
                <div class="progress flex-grow-1 me-3" style="height: 20px;">
                    <div class="progress-bar bg-{color}" style="width: {score*100:.0f}%">{score:.2f}</div>
                </div>
                <span class="badge bg-{color} fs-6">{score:.2f}</span>
            </div>
            <p class="text-muted small mb-0">{reasoning}</p>
            {warnings_html}
            {actions_html}
        </div>
    </div>
    """)


@router.post("/summary/{event_id}")
async def generate_summary(event_id: int, admin=Depends(require_admin), db: Session = Depends(get_db)):
    """Generate AI summary for an event."""
    summary = await ai_analysis.generate_event_summary(db, event_id)
    event = db.query(Event).get(event_id)
    if event:
        event.ai_summary = summary
        db.commit()
    return HTMLResponse(f"""
    <div class="card border-0 shadow-sm">
        <div class="card-body">
            <h6 class="mb-2"><i class="bi bi-file-text me-1"></i> KI-Zusammenfassung</h6>
            <p class="mb-0">{summary}</p>
        </div>
    </div>
    """)


# --- HTMX widget endpoints for dashboard ---

@router.get("/widget/engagement")
async def widget_engagement(admin=Depends(require_admin), db: Session = Depends(get_db)):
    """Dashboard widget: top companies for engagement analysis."""
    companies = (
        db.query(Company)
        .filter(Company.is_active == True)
        .order_by(Company.name)
        .limit(5)
        .all()
    )

    if not companies:
        return HTMLResponse('<p class="text-muted small mb-0">Keine Unternehmen vorhanden.</p>')

    rows = ""
    for c in companies:
        rows += f"""
        <div class="d-flex justify-content-between align-items-center mb-2">
            <span class="small">{c.name}</span>
            <button class="btn btn-sm btn-outline-primary"
                    hx-post="/ai/engagement/{c.id}"
                    hx-target="#engagement-result-{c.id}"
                    hx-swap="innerHTML">
                <i class="bi bi-cpu"></i> Berechnen
            </button>
        </div>
        <div id="engagement-result-{c.id}" class="mb-2"></div>
        """

    return HTMLResponse(rows)


@router.get("/widget/churn")
async def widget_churn(admin=Depends(require_admin), db: Session = Depends(get_db)):
    """Dashboard widget: churn risk alerts."""
    companies = (
        db.query(Company)
        .filter(Company.is_active == True)
        .order_by(Company.name)
        .limit(5)
        .all()
    )

    if not companies:
        return HTMLResponse('<p class="text-muted small mb-0">Keine Unternehmen vorhanden.</p>')

    rows = ""
    for c in companies:
        rows += f"""
        <div class="d-flex justify-content-between align-items-center mb-2">
            <span class="small">{c.name}</span>
            <button class="btn btn-sm btn-outline-warning"
                    hx-post="/ai/churn/{c.id}"
                    hx-target="#churn-result-{c.id}"
                    hx-swap="innerHTML">
                <i class="bi bi-cpu"></i> Pruefen
            </button>
        </div>
        <div id="churn-result-{c.id}" class="mb-2"></div>
        """

    return HTMLResponse(rows)


def _score_color(score: float) -> str:
    """Return Bootstrap color class based on score (higher = better)."""
    if score >= 0.7:
        return "success"
    elif score >= 0.4:
        return "warning"
    return "danger"


def _score_color_inverted(score: float) -> str:
    """Return Bootstrap color class based on score (higher = worse, for risk)."""
    if score >= 0.7:
        return "danger"
    elif score >= 0.4:
        return "warning"
    return "success"
