"""
Scoring-Service fuer AG City Veranstaltungs-Zulassungen.

Berechnet einen Priority-Score (0-100) fuer jede Anmeldung basierend auf:
1. Teilnahme-Zuverlaessigkeit (No-Show-Quote)
2. Mitgliedsstatus & Beitragstreue
3. Veranstaltungs-Engagement (Anzahl besuchter Events)
4. Branchenvielfalt (Diversitaet foerdern)
5. Wartezeit (laenger nicht teilgenommen = hoehere Prioritaet)
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.registration import EventRegistration
from app.models.company import Company, ContactPerson
from app.models.event import Event


def compute_priority_score(db: Session, registration_id: int) -> dict:
    """Compute priority score for a registration. Returns dict with score + reasons."""
    reg = db.query(EventRegistration).get(registration_id)
    if not reg:
        return {"score": 0, "reasons": [], "summary": "Anmeldung nicht gefunden."}

    reasons = []
    score_parts = {}

    # --- 1. Zuverlaessigkeits-Score (max 30 Punkte) ---
    email = reg.email
    past = (
        db.query(EventRegistration)
        .filter(
            EventRegistration.email == email,
            EventRegistration.event_id != reg.event_id,
            EventRegistration.status.in_(["zugelassen", "bestaetigt", "confirmed"]),
        )
        .all()
    )

    if past:
        attended = sum(1 for r in past if r.attendance == "attended")
        no_shows = sum(1 for r in past if r.attendance == "no_show")
        total_tracked = attended + no_shows

        if total_tracked > 0:
            reliability = attended / total_tracked
            reliability_pts = round(reliability * 30)
            if no_shows == 0:
                reasons.append(f"+{reliability_pts} Pkt: Zuverlaessig - {attended}/{total_tracked} Teilnahmen, keine No-Shows")
            else:
                reasons.append(f"+{reliability_pts} Pkt: Zuverlaessigkeit {attended}/{total_tracked} ({no_shows} No-Show{'s' if no_shows > 1 else ''})")
        else:
            reliability_pts = 20  # neutral if no tracking data
            reasons.append("+20 Pkt: Keine Teilnahme-Historie (neutral)")
    else:
        reliability_pts = 15  # new person, slightly lower
        reasons.append("+15 Pkt: Erstanmeldung (keine Historie)")

    score_parts["zuverlaessigkeit"] = reliability_pts

    # --- 2. Mitgliedsstatus & Beitrag (max 25 Punkte) ---
    member_pts = 0
    if reg.company_id:
        company = db.query(Company).get(reg.company_id)
        if company and company.is_active:
            member_pts += 15
            reasons.append("+15 Pkt: Aktives Mitglied")

            # Beitrag bezahlt?
            from app.models.membership import MembershipFee
            current_year = datetime.utcnow().year
            fee = (
                db.query(MembershipFee)
                .filter(
                    MembershipFee.company_id == company.id,
                    MembershipFee.year == current_year,
                )
                .first()
            )
            if fee and fee.status == "paid":
                member_pts += 10
                reasons.append("+10 Pkt: Mitgliedsbeitrag bezahlt")
            elif fee and fee.status in ("outstanding", "overdue"):
                reasons.append("+0 Pkt: Mitgliedsbeitrag ausstehend")
        elif company:
            member_pts += 5
            reasons.append("+5 Pkt: Inaktives/ehemaliges Mitglied")
    elif reg.is_member:
        member_pts += 10
        reasons.append("+10 Pkt: Gibt an, Mitglied zu sein (nicht verknuepft)")
    else:
        member_pts += 3
        reasons.append("+3 Pkt: Nicht-Mitglied (Gast)")

    score_parts["mitgliedschaft"] = member_pts

    # --- 3. Engagement-Score (max 20 Punkte) ---
    total_attended = (
        db.query(func.count(EventRegistration.id))
        .filter(
            EventRegistration.email == email,
            EventRegistration.attendance == "attended",
        )
        .scalar() or 0
    )

    if total_attended >= 10:
        engagement_pts = 20
        reasons.append(f"+20 Pkt: Sehr aktiv ({total_attended} Veranstaltungen besucht)")
    elif total_attended >= 5:
        engagement_pts = 15
        reasons.append(f"+15 Pkt: Aktiv ({total_attended} Veranstaltungen besucht)")
    elif total_attended >= 2:
        engagement_pts = 10
        reasons.append(f"+10 Pkt: Gelegentlich ({total_attended} Veranstaltungen besucht)")
    elif total_attended >= 1:
        engagement_pts = 7
        reasons.append(f"+7 Pkt: Einmal teilgenommen")
    else:
        engagement_pts = 3
        reasons.append("+3 Pkt: Noch nie teilgenommen")

    score_parts["engagement"] = engagement_pts

    # --- 4. Wartezeit / Fairness (max 15 Punkte) ---
    # Wer laenger nicht dran war, bekommt mehr Punkte
    last_attended = (
        db.query(EventRegistration)
        .join(Event)
        .filter(
            EventRegistration.email == email,
            EventRegistration.attendance == "attended",
        )
        .order_by(Event.event_date.desc())
        .first()
    )

    if last_attended and last_attended.event:
        days_since = (datetime.utcnow() - last_attended.event.event_date).days
        if days_since > 180:
            fairness_pts = 15
            reasons.append(f"+15 Pkt: Lange nicht dabei (>{days_since} Tage)")
        elif days_since > 90:
            fairness_pts = 10
            reasons.append(f"+10 Pkt: Letzte Teilnahme vor {days_since} Tagen")
        elif days_since > 30:
            fairness_pts = 7
            reasons.append(f"+7 Pkt: Vor kurzem teilgenommen ({days_since} Tage)")
        else:
            fairness_pts = 3
            reasons.append(f"+3 Pkt: Kuerzlich teilgenommen ({days_since} Tage)")
    else:
        fairness_pts = 12
        reasons.append("+12 Pkt: Noch nie teilgenommen (hohe Fairness-Prioritaet)")

    score_parts["fairness"] = fairness_pts

    # --- 5. Branchen-Diversitaet (max 10 Punkte) ---
    # Pruefen ob die Branche des Anmelders bei dieser Veranstaltung schon stark vertreten ist
    event_regs = (
        db.query(EventRegistration)
        .filter(
            EventRegistration.event_id == reg.event_id,
            EventRegistration.status.in_(["zugelassen", "bestaetigt", "confirmed"]),
            EventRegistration.id != reg.id,
        )
        .all()
    )

    if reg.branche or (reg.company_id and db.query(Company).get(reg.company_id)):
        company_branche = reg.branche
        if not company_branche and reg.company_id:
            comp = db.query(Company).get(reg.company_id)
            if comp:
                company_branche = comp.branche

        if company_branche:
            same_branche = sum(1 for r in event_regs if _get_branche(db, r) == company_branche)
            if same_branche == 0:
                diversity_pts = 10
                reasons.append(f"+10 Pkt: Neue Branche fuer diese Veranstaltung ({company_branche})")
            elif same_branche <= 2:
                diversity_pts = 7
                reasons.append(f"+7 Pkt: Branche wenig vertreten ({company_branche}: {same_branche}x)")
            else:
                diversity_pts = 3
                reasons.append(f"+3 Pkt: Branche bereits gut vertreten ({company_branche}: {same_branche}x)")
        else:
            diversity_pts = 5
            reasons.append("+5 Pkt: Keine Branche angegeben")
    else:
        diversity_pts = 5
        reasons.append("+5 Pkt: Keine Brancheninfo")

    score_parts["diversitaet"] = diversity_pts

    # --- Gesamt-Score ---
    total = sum(score_parts.values())

    # Summary
    summary_parts = []
    if reliability_pts >= 25:
        summary_parts.append("sehr zuverlaessig")
    elif reliability_pts < 15:
        summary_parts.append("No-Show Risiko")
    if member_pts >= 20:
        summary_parts.append("aktives zahlendes Mitglied")
    elif member_pts <= 5:
        summary_parts.append("Gast/Nicht-Mitglied")
    if engagement_pts >= 15:
        summary_parts.append("sehr engagiert")
    summary = ", ".join(summary_parts) if summary_parts else "Standard-Profil"

    return {
        "score": total,
        "max_score": 100,
        "parts": score_parts,
        "reasons": reasons,
        "summary": f"Score {total}/100: {summary}",
    }


def score_all_registrations(db: Session, event_id: int) -> list[dict]:
    """Score all 'angemeldet' registrations for an event and return ranked list."""
    registrations = (
        db.query(EventRegistration)
        .filter(
            EventRegistration.event_id == event_id,
            EventRegistration.status.in_(["angemeldet", "pending"]),
        )
        .all()
    )

    results = []
    for reg in registrations:
        result = compute_priority_score(db, reg.id)
        # Save score to DB
        reg.priority_score = result["score"]
        reg.priority_reason = "\n".join(result["reasons"])
        results.append({"registration": reg, **result})

    db.commit()

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def get_event_analytics(db: Session, event_id: int) -> dict:
    """Analyze a past event."""
    event = db.query(Event).get(event_id)
    if not event:
        return {}

    regs = (
        db.query(EventRegistration)
        .filter(EventRegistration.event_id == event_id)
        .all()
    )

    total = len(regs)
    confirmed = sum(1 for r in regs if r.status in ("zugelassen", "bestaetigt", "confirmed"))
    attended = sum(1 for r in regs if r.attendance == "attended")
    no_shows = sum(1 for r in regs if r.attendance == "no_show")
    rejected = sum(1 for r in regs if r.status in ("abgelehnt", "rejected"))

    # Branchen-Verteilung
    branchen = {}
    for r in regs:
        b = _get_branche(db, r) or "Unbekannt"
        branchen[b] = branchen.get(b, 0) + 1

    # Mitglieder vs Gaeste
    members = sum(1 for r in regs if r.is_member or r.company_id)
    guests = total - members

    # Top No-Show Unternehmen
    no_show_companies = {}
    for r in regs:
        if r.attendance == "no_show" and r.organization:
            no_show_companies[r.organization] = no_show_companies.get(r.organization, 0) + 1

    return {
        "event": event,
        "total_registrations": total,
        "confirmed": confirmed,
        "attended": attended,
        "no_shows": no_shows,
        "no_show_rate": round(no_shows / max(confirmed, 1) * 100, 1),
        "rejected": rejected,
        "attendance_rate": round(attended / max(confirmed, 1) * 100, 1),
        "branchen": dict(sorted(branchen.items(), key=lambda x: -x[1])),
        "members": members,
        "guests": guests,
        "member_ratio": round(members / max(total, 1) * 100, 1),
        "no_show_companies": dict(sorted(no_show_companies.items(), key=lambda x: -x[1])[:10]),
    }


def get_company_event_history(db: Session, company_id: int) -> dict:
    """Get event history for a company."""
    regs = (
        db.query(EventRegistration)
        .join(Event)
        .filter(EventRegistration.company_id == company_id)
        .order_by(Event.event_date.desc())
        .all()
    )

    total = len(regs)
    attended = sum(1 for r in regs if r.attendance == "attended")
    no_shows = sum(1 for r in regs if r.attendance == "no_show")

    return {
        "total_registrations": total,
        "attended": attended,
        "no_shows": no_shows,
        "reliability_pct": round(attended / max(attended + no_shows, 1) * 100, 1),
        "history": regs,
    }


def get_person_event_history(db: Session, email: str) -> dict:
    """Get event history for a person by email."""
    regs = (
        db.query(EventRegistration)
        .join(Event)
        .filter(EventRegistration.email == email)
        .order_by(Event.event_date.desc())
        .all()
    )

    total = len(regs)
    attended = sum(1 for r in regs if r.attendance == "attended")
    no_shows = sum(1 for r in regs if r.attendance == "no_show")

    return {
        "total_registrations": total,
        "attended": attended,
        "no_shows": no_shows,
        "reliability_pct": round(attended / max(attended + no_shows, 1) * 100, 1),
        "history": regs,
    }


def _get_branche(db: Session, reg: EventRegistration) -> str | None:
    """Get branche for a registration, checking company if needed."""
    if reg.branche:
        return reg.branche
    if reg.company_id:
        comp = db.query(Company).get(reg.company_id)
        if comp:
            return comp.branche
    return None
