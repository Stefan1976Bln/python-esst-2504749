from datetime import date, datetime

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Company, MembershipFee, PaymentRecord
from app.routers.admin_auth import require_admin

router = APIRouter(prefix="/fees", tags=["fees"])
templates = Jinja2Templates(directory="app/templates")


@router.get("")
async def fees_overview(
    request: Request,
    year: int | None = None,
    admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Fee management overview with year filter."""
    # Available years for filter
    available_years = (
        db.query(MembershipFee.year)
        .distinct()
        .order_by(MembershipFee.year.desc())
        .all()
    )
    available_years = [y[0] for y in available_years]

    if not year:
        year = datetime.utcnow().year

    # Query fees for the selected year
    fees = (
        db.query(MembershipFee)
        .filter(MembershipFee.year == year)
        .join(Company)
        .order_by(Company.name)
        .all()
    )

    # Summary stats
    total_due = sum(f.amount_due for f in fees)
    total_paid = sum(f.amount_paid for f in fees)
    total_outstanding = total_due - total_paid
    collection_pct = round((total_paid / total_due * 100) if total_due > 0 else 0, 1)

    return templates.TemplateResponse("membership/overview.html", {
        "request": request,
        "active_page": "fees",
        "admin_user": admin.username,
        "fees": fees,
        "year": year,
        "available_years": available_years,
        "total_due": total_due,
        "total_paid": total_paid,
        "total_outstanding": total_outstanding,
        "collection_pct": collection_pct,
    })


@router.post("/record-payment")
async def record_payment(
    request: Request,
    fee_id: int = Form(...),
    amount: float = Form(...),
    payment_date: str = Form(...),
    payment_method: str = Form(""),
    reference: str = Form(""),
    admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Record a payment for a membership fee (HTMX)."""
    fee = db.query(MembershipFee).get(fee_id)
    if not fee:
        return HTMLResponse('<div class="alert alert-danger">Beitrag nicht gefunden.</div>')

    # Create payment record
    payment = PaymentRecord(
        fee_id=fee.id,
        amount=amount,
        payment_date=datetime.strptime(payment_date, "%Y-%m-%d").date(),
        payment_method=payment_method or None,
        reference=reference or None,
    )
    db.add(payment)

    # Update fee
    fee.amount_paid = fee.amount_paid + amount
    if fee.amount_paid >= fee.amount_due:
        fee.status = "paid"
    elif fee.amount_paid > 0:
        fee.status = "partial"

    db.commit()

    # Return updated row via HTMX
    status_badge = _status_badge(fee.status)
    remaining = fee.amount_due - fee.amount_paid
    return HTMLResponse(f"""
    <tr id="fee-row-{fee.id}">
        <td>{fee.company.name}</td>
        <td>{fee.amount_due:.2f} &euro;</td>
        <td>{fee.amount_paid:.2f} &euro;</td>
        <td>{remaining:.2f} &euro;</td>
        <td>{status_badge}</td>
        <td>
            <button class="btn btn-sm btn-outline-success"
                    data-bs-toggle="modal"
                    data-bs-target="#paymentModal"
                    onclick="document.getElementById('modal_fee_id').value='{fee.id}';
                             document.getElementById('modal_company_name').textContent='{fee.company.name}';
                             document.getElementById('modal_remaining').textContent='{remaining:.2f}';">
                <i class="bi bi-plus-circle"></i> Zahlung
            </button>
        </td>
    </tr>
    """)


def _status_badge(status: str) -> str:
    badges = {
        "paid": '<span class="badge bg-success">Bezahlt</span>',
        "partial": '<span class="badge bg-info">Teilweise</span>',
        "outstanding": '<span class="badge bg-warning text-dark">Offen</span>',
        "overdue": '<span class="badge bg-danger">Ueberfaellig</span>',
    }
    return badges.get(status, f'<span class="badge bg-secondary">{status}</span>')
