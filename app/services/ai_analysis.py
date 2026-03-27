import json
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.config import settings
from app.models.registration import EventRegistration
from app.models.event import Event
from app.models.company import Company, ContactPerson
from app.models.ai import AIScore

logger = logging.getLogger(__name__)


async def _call_claude(system_prompt: str, user_prompt: str) -> str:
    """Call Claude API and return the response text."""
    if not settings.CLAUDE_API_KEY:
        logger.warning("Claude API key not configured, returning mock response")
        return json.dumps({"score": 0.5, "reasoning": "KI-Analyse nicht verfuegbar (API-Key fehlt)"})

    import anthropic

    client = anthropic.AsyncAnthropic(api_key=settings.CLAUDE_API_KEY)
    message = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return message.content[0].text


async def compute_reliability_score(db: Session, email: str) -> dict:
    """Compute reliability score based on past attendance behavior."""
    past_registrations = (
        db.query(EventRegistration)
        .filter(EventRegistration.email == email)
        .all()
    )

    total = len(past_registrations)
    if total == 0:
        return {"score": 0.5, "reasoning": "Keine Teilnahmehistorie vorhanden - Neutraler Score."}

    confirmed = sum(1 for r in past_registrations if r.status == "confirmed")
    attended = sum(1 for r in past_registrations if r.attendance == "attended")
    no_shows = sum(1 for r in past_registrations if r.attendance == "no_show")

    history_summary = (
        f"Gesamtanmeldungen: {total}, "
        f"Bestaetigt: {confirmed}, "
        f"Teilgenommen: {attended}, "
        f"No-Shows: {no_shows}"
    )

    system_prompt = """Du bist ein Analyse-Assistent fuer Veranstaltungsmanagement.
Analysiere das Teilnahmeverhalten und gib einen Zuverlaessigkeits-Score.
Antworte IMMER als JSON: {"score": 0.0-1.0, "reasoning": "Begruendung auf Deutsch"}"""

    user_prompt = f"""Teilnahmehistorie fuer {email}:
{history_summary}

Berechne einen Zuverlaessigkeits-Score (0.0 = sehr unzuverlaessig, 1.0 = sehr zuverlaessig).
Beruecksichtige: No-Show-Quote, Gesamtanzahl der Teilnahmen, Trend."""

    try:
        response = await _call_claude(system_prompt, user_prompt)
        result = json.loads(response)
        return {"score": float(result.get("score", 0.5)), "reasoning": result.get("reasoning", "")}
    except Exception as e:
        # Fallback: simple calculation
        if confirmed > 0:
            score = attended / confirmed if confirmed > 0 else 0.5
        else:
            score = 0.5
        return {"score": round(score, 2), "reasoning": f"Berechnet: {attended}/{confirmed} Teilnahmen. {str(e)}"}


async def compute_suitability_score(db: Session, registration_id: int) -> dict:
    """Compute how well a registrant fits an event based on profile and event topic."""
    reg = db.query(EventRegistration).get(registration_id)
    if not reg:
        return {"score": 0.5, "reasoning": "Anmeldung nicht gefunden."}

    event = reg.event

    # Gather registrant profile
    profile_parts = [f"Name: {reg.full_name}"]
    if reg.organization:
        profile_parts.append(f"Organisation: {reg.organization}")
    if reg.branche:
        profile_parts.append(f"Branche: {reg.branche}")
    if reg.motivation:
        profile_parts.append(f"Motivation: {reg.motivation}")

    # Check past events attended
    past_events = (
        db.query(EventRegistration)
        .filter(
            EventRegistration.email == reg.email,
            EventRegistration.attendance == "attended",
        )
        .all()
    )
    if past_events:
        event_types = [r.event.event_type for r in past_events if r.event and r.event.event_type]
        if event_types:
            profile_parts.append(f"Besuchte Veranstaltungstypen: {', '.join(set(event_types))}")

    profile = "\n".join(profile_parts)

    system_prompt = """Du bist ein KI-Assistent fuer AG City Veranstaltungsmanagement.
Analysiere, wie gut ein Teilnehmer zu einer Veranstaltung passt.
Antworte IMMER als JSON: {"score": 0.0-1.0, "reasoning": "Begruendung auf Deutsch", "recommendation": "approve/reject/waitlist"}"""

    user_prompt = f"""Veranstaltung:
Titel: {event.title}
Typ: {event.event_type or 'Allgemein'}
Beschreibung: {event.description or 'Keine Beschreibung'}

Teilnehmer-Profil:
{profile}

Bewerte die Passung (0.0 = passt gar nicht, 1.0 = perfekte Passung).
Beruecksichtige: Branche, Interessen, vergangene Veranstaltungen, Motivation."""

    try:
        response = await _call_claude(system_prompt, user_prompt)
        result = json.loads(response)
        return {
            "score": float(result.get("score", 0.5)),
            "reasoning": result.get("reasoning", ""),
            "recommendation": result.get("recommendation", "waitlist"),
        }
    except Exception as e:
        return {"score": 0.5, "reasoning": f"Analyse-Fehler: {str(e)}"}


async def compute_engagement_score(db: Session, company_id: int) -> dict:
    """Compute engagement score for a member company."""
    company = db.query(Company).get(company_id)
    if not company:
        return {"score": 0.0, "reasoning": "Unternehmen nicht gefunden."}

    # Gather data
    total_registrations = (
        db.query(EventRegistration)
        .filter(EventRegistration.company_id == company_id)
        .count()
    )
    attended = (
        db.query(EventRegistration)
        .filter(EventRegistration.company_id == company_id, EventRegistration.attendance == "attended")
        .count()
    )
    no_shows = (
        db.query(EventRegistration)
        .filter(EventRegistration.company_id == company_id, EventRegistration.attendance == "no_show")
        .count()
    )

    # Fee data
    from app.models.membership import MembershipFee
    fees = db.query(MembershipFee).filter(MembershipFee.company_id == company_id).all()
    paid_fees = sum(1 for f in fees if f.status == "paid")
    total_fees = len(fees)

    profile = f"""Unternehmen: {company.name}
Branche: {company.branche or 'Unbekannt'}
Mitglied seit: {company.membership_since or 'Unbekannt'}
Veranstaltungsanmeldungen: {total_registrations}
Teilnahmen: {attended}
No-Shows: {no_shows}
Beitragszahlungen: {paid_fees}/{total_fees} bezahlt"""

    system_prompt = """Du bist ein KI-Assistent fuer Mitglieder-Engagement-Analyse.
Bewerte das Engagement eines Mitgliedsunternehmens.
Antworte als JSON: {"score": 0.0-1.0, "reasoning": "Begruendung", "recommendations": ["Empfehlung 1", "Empfehlung 2"]}"""

    try:
        response = await _call_claude(system_prompt, f"Analysiere das Engagement:\n{profile}")
        result = json.loads(response)
        return result
    except Exception as e:
        # Fallback calculation
        if total_registrations > 0:
            score = attended / total_registrations * 0.7 + (paid_fees / max(total_fees, 1)) * 0.3
        else:
            score = 0.3
        return {"score": round(score, 2), "reasoning": f"Automatisch berechnet. {str(e)}", "recommendations": []}


async def compute_churn_risk(db: Session, company_id: int) -> dict:
    """Predict churn risk for a member company."""
    company = db.query(Company).get(company_id)
    if not company:
        return {"score": 0.0, "reasoning": "Unternehmen nicht gefunden."}

    from app.models.membership import MembershipFee

    # Recent activity
    recent_registrations = (
        db.query(EventRegistration)
        .filter(EventRegistration.company_id == company_id)
        .order_by(EventRegistration.registered_at.desc())
        .limit(10)
        .all()
    )

    overdue_fees = (
        db.query(MembershipFee)
        .filter(MembershipFee.company_id == company_id, MembershipFee.status.in_(["outstanding", "overdue"]))
        .all()
    )

    profile = f"""Unternehmen: {company.name}
Mitglied seit: {company.membership_since or 'Unbekannt'}
Aktiv: {company.is_active}
Letzte Anmeldungen: {len(recent_registrations)}
Offene Beitraege: {len(overdue_fees)}
Ausstehender Betrag: {sum(f.amount_due - f.amount_paid for f in overdue_fees):.2f} EUR"""

    system_prompt = """Du bist ein KI-Assistent fuer Churn-Prognose bei Vereinsmitgliedern.
Bewerte das Abwanderungsrisiko eines Mitgliedsunternehmens.
Antworte als JSON: {"score": 0.0-1.0, "reasoning": "Begruendung", "warning_signs": ["Zeichen 1"], "retention_actions": ["Massnahme 1"]}
Score: 0.0 = kein Risiko, 1.0 = sehr hohes Abwanderungsrisiko."""

    try:
        response = await _call_claude(system_prompt, f"Analysiere Churn-Risiko:\n{profile}")
        return json.loads(response)
    except Exception as e:
        score = min(1.0, len(overdue_fees) * 0.3 + (0.3 if len(recent_registrations) == 0 else 0))
        return {"score": round(score, 2), "reasoning": f"Automatisch berechnet. {str(e)}",
                "warning_signs": [], "retention_actions": []}


async def generate_event_summary(db: Session, event_id: int) -> str:
    """Generate an AI summary for a past event."""
    event = db.query(Event).get(event_id)
    if not event:
        return "Veranstaltung nicht gefunden."

    attendees = (
        db.query(EventRegistration)
        .filter(EventRegistration.event_id == event_id, EventRegistration.attendance == "attended")
        .all()
    )

    attendee_info = "\n".join(
        f"- {a.full_name} ({a.organization or 'Unbekannt'}, {a.branche or 'Unbekannt'})"
        for a in attendees
    )

    prompt = f"""Veranstaltung: {event.title}
Typ: {event.event_type or 'Allgemein'}
Datum: {event.event_date.strftime('%d.%m.%Y')}
Ort: {event.location or 'Unbekannt'}
Beschreibung: {event.description or 'Keine Beschreibung'}
Anzahl Teilnehmer: {len(attendees)}

Teilnehmer:
{attendee_info or 'Keine Teilnehmer erfasst'}

Erstelle eine professionelle Zusammenfassung der Veranstaltung auf Deutsch (3-5 Saetze),
geeignet fuer einen Newsletter oder internen Bericht."""

    try:
        return await _call_claude(
            "Du bist ein professioneller Texter fuer Veranstaltungsberichte.",
            prompt,
        )
    except Exception as e:
        return f"Zusammenfassung konnte nicht erstellt werden: {str(e)}"


async def suggest_events_for_member(db: Session, company_id: int) -> list[dict]:
    """Suggest upcoming events that match a company's profile."""
    company = db.query(Company).get(company_id)
    if not company:
        return []

    upcoming_events = (
        db.query(Event)
        .filter(Event.event_date > datetime.utcnow(), Event.is_published == True)
        .all()
    )

    if not upcoming_events:
        return []

    events_text = "\n".join(
        f"- ID {e.id}: {e.title} ({e.event_type or 'Allgemein'}): {e.description or 'Keine Beschreibung'}"
        for e in upcoming_events
    )

    # Past attendance
    past = (
        db.query(EventRegistration)
        .filter(EventRegistration.company_id == company_id, EventRegistration.attendance == "attended")
        .all()
    )
    past_types = [r.event.event_type for r in past if r.event and r.event.event_type]

    prompt = f"""Unternehmen: {company.name}
Branche: {company.branche or 'Unbekannt'}
Groesse: {company.company_size or 'Unbekannt'}
Fruehere Veranstaltungstypen: {', '.join(set(past_types)) or 'Keine'}

Kommende Veranstaltungen:
{events_text}

Empfehle die passendsten Veranstaltungen fuer dieses Unternehmen.
Antworte als JSON-Array: [{{"event_id": 1, "relevance": 0.9, "reason": "Begruendung"}}]"""

    try:
        response = await _call_claude(
            "Du bist ein KI-Assistent fuer personalisierte Veranstaltungsempfehlungen.",
            prompt,
        )
        return json.loads(response)
    except Exception:
        return [{"event_id": e.id, "relevance": 0.5, "reason": "Automatische Empfehlung"} for e in upcoming_events[:3]]
