from datetime import datetime

from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Company, Event, EventRegistration, MembershipFee
from app.routers.admin_auth import require_admin

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard")
async def dashboard(request: Request, admin=Depends(require_admin), db: Session = Depends(get_db)):
    # KPI: Total companies
    total_companies = db.query(func.count(Company.id)).scalar() or 0

    # KPI: Active members
    active_members = (
        db.query(func.count(Company.id))
        .filter(Company.is_active == True)
        .scalar() or 0
    )

    # KPI: Upcoming events
    upcoming_events = (
        db.query(func.count(Event.id))
        .filter(Event.event_date >= datetime.utcnow())
        .scalar() or 0
    )

    # KPI: Pending registrations
    pending_registrations = (
        db.query(func.count(EventRegistration.id))
        .filter(EventRegistration.status == "pending")
        .scalar() or 0
    )

    # KPI: Outstanding fees total
    outstanding_total = (
        db.query(func.coalesce(func.sum(MembershipFee.amount_due - MembershipFee.amount_paid), 0.0))
        .filter(MembershipFee.status != "paid")
        .scalar() or 0.0
    )

    # Fee collection stats for progress bar
    total_due = db.query(func.coalesce(func.sum(MembershipFee.amount_due), 0.0)).scalar() or 0.0
    total_paid = db.query(func.coalesce(func.sum(MembershipFee.amount_paid), 0.0)).scalar() or 0.0
    fee_collection_pct = round((total_paid / total_due * 100) if total_due > 0 else 0, 1)

    # Fee status breakdown
    fees_paid_count = db.query(func.count(MembershipFee.id)).filter(MembershipFee.status == "paid").scalar() or 0
    fees_partial_count = db.query(func.count(MembershipFee.id)).filter(MembershipFee.status == "partial").scalar() or 0
    fees_outstanding_count = db.query(func.count(MembershipFee.id)).filter(MembershipFee.status == "outstanding").scalar() or 0
    fees_overdue_count = db.query(func.count(MembershipFee.id)).filter(MembershipFee.status == "overdue").scalar() or 0
    fees_total_count = max(fees_paid_count + fees_partial_count + fees_outstanding_count + fees_overdue_count, 1)

    # Recent registrations
    recent_registrations = (
        db.query(EventRegistration)
        .order_by(EventRegistration.registered_at.desc())
        .limit(10)
        .all()
    )

    return templates.TemplateResponse("dashboard/index.html", {
        "request": request,
        "active_page": "dashboard",
        "admin_user": admin.username,
        "total_companies": total_companies,
        "active_members": active_members,
        "upcoming_events": upcoming_events,
        "pending_registrations": pending_registrations,
        "outstanding_total": outstanding_total,
        "fee_collection_pct": fee_collection_pct,
        "total_due": total_due,
        "total_paid": total_paid,
        "fees_paid_count": fees_paid_count,
        "fees_partial_count": fees_partial_count,
        "fees_outstanding_count": fees_outstanding_count,
        "fees_overdue_count": fees_overdue_count,
        "fees_total_count": fees_total_count,
        "recent_registrations": recent_registrations,
    })
