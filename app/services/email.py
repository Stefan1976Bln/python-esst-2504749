import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sqlalchemy.orm import Session

from app.config import settings
from app.models.ai import EmailLog

logger = logging.getLogger(__name__)


async def send_email(db: Session, to_email: str, subject: str, html_body: str, template_name: str = "") -> bool:
    """Send an email and log it. Returns True if successful."""
    log_entry = EmailLog(
        recipient_email=to_email,
        subject=subject,
        template_name=template_name,
    )

    try:
        if not settings.SMTP_HOST:
            logger.warning(f"SMTP not configured. Would send to {to_email}: {subject}")
            log_entry.status = "skipped"
            log_entry.error_message = "SMTP not configured"
            db.add(log_entry)
            db.commit()
            return True

        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html"))

        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=True,
        )

        log_entry.status = "sent"
        db.add(log_entry)
        db.commit()
        logger.info(f"Email sent to {to_email}: {subject}")
        return True

    except Exception as e:
        log_entry.status = "failed"
        log_entry.error_message = str(e)
        db.add(log_entry)
        db.commit()
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


def registration_confirmation_html(name: str, event_title: str, event_date: str) -> str:
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2c3e50;">Anmeldebestaetigung</h2>
        <p>Sehr geehrte/r {name},</p>
        <p>vielen Dank fuer Ihre Anmeldung zur Veranstaltung:</p>
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0;">
            <strong>{event_title}</strong><br>
            Datum: {event_date}
        </div>
        <p>Ihre Anmeldung ist eingegangen und wird geprueft.
        Sie erhalten eine separate Bestaetigung, sobald Ihr Platz zugesichert wurde.</p>
        <p>Mit freundlichen Gruessen,<br>Ihr AG City Team</p>
    </body>
    </html>
    """


def approval_notification_html(name: str, event_title: str, event_date: str, location: str) -> str:
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #27ae60;">Teilnahme bestaetigt!</h2>
        <p>Sehr geehrte/r {name},</p>
        <p>wir freuen uns, Ihnen mitzuteilen, dass Ihre Teilnahme bestaetigt wurde:</p>
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0;">
            <strong>{event_title}</strong><br>
            Datum: {event_date}<br>
            Ort: {location or 'Wird noch bekannt gegeben'}
        </div>
        <p>Wir freuen uns auf Sie!</p>
        <p>Mit freundlichen Gruessen,<br>Ihr AG City Team</p>
    </body>
    </html>
    """


def rejection_notification_html(name: str, event_title: str) -> str:
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #e74c3c;">Leider kein Platz verfuegbar</h2>
        <p>Sehr geehrte/r {name},</p>
        <p>leider muessen wir Ihnen mitteilen, dass fuer die Veranstaltung
        <strong>{event_title}</strong> keine Plaetze mehr verfuegbar sind.</p>
        <p>Wir halten Sie gerne ueber zukuenftige Veranstaltungen auf dem Laufenden.</p>
        <p>Mit freundlichen Gruessen,<br>Ihr AG City Team</p>
    </body>
    </html>
    """
