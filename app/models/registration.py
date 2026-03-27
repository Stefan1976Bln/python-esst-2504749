from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class EventRegistration(Base):
    __tablename__ = "event_registrations"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    contact_person_id: Mapped[int | None] = mapped_column(ForeignKey("contact_persons.id", ondelete="SET NULL"))
    company_id: Mapped[int | None] = mapped_column(ForeignKey("companies.id", ondelete="SET NULL"))

    # Always captured
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    organization: Mapped[str | None] = mapped_column(String(255))
    branche: Mapped[str | None] = mapped_column(String(100))
    is_member: Mapped[bool] = mapped_column(Boolean, default=False)
    motivation: Mapped[str | None] = mapped_column(Text)

    # Status workflow:
    #   angemeldet -> zugelassen / abgelehnt / warteliste
    #   (legacy: pending/confirmed/rejected/waitlisted still supported)
    # Valid values: angemeldet, zugelassen, bestaetigt, abgelehnt, warteliste, storniert
    status: Mapped[str] = mapped_column(String(20), default="angemeldet")

    # Attendance: null = not yet tracked, attended = was there, no_show = didn't come
    attendance: Mapped[str | None] = mapped_column(String(20))
    checked_in_at: Mapped[datetime | None] = mapped_column(DateTime)
    admin_notes: Mapped[str | None] = mapped_column(Text)

    # Scoring fields
    ai_suitability_score: Mapped[float | None] = mapped_column(Float)
    ai_suitability_reason: Mapped[str | None] = mapped_column(Text)
    ai_reliability_score: Mapped[float | None] = mapped_column(Float)
    ai_reliability_reason: Mapped[str | None] = mapped_column(Text)
    priority_score: Mapped[float | None] = mapped_column(Float)  # Combined ranking score 0-100
    priority_reason: Mapped[str | None] = mapped_column(Text)  # Human-readable explanation

    registered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    event: Mapped["Event"] = relationship(back_populates="registrations")
    contact_person: Mapped["ContactPerson | None"] = relationship(back_populates="registrations")
    company: Mapped["Company | None"] = relationship(back_populates="registrations")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def status_label(self) -> str:
        labels = {
            "angemeldet": "Angemeldet",
            "zugelassen": "Zugelassen",
            "bestaetigt": "Bestaetigt",
            "abgelehnt": "Abgelehnt",
            "warteliste": "Warteliste",
            "storniert": "Storniert",
            # Legacy
            "pending": "Angemeldet",
            "confirmed": "Zugelassen",
            "rejected": "Abgelehnt",
            "waitlisted": "Warteliste",
        }
        return labels.get(self.status, self.status)

    @property
    def status_color(self) -> str:
        colors = {
            "angemeldet": "info",
            "zugelassen": "success",
            "bestaetigt": "success",
            "abgelehnt": "danger",
            "warteliste": "warning",
            "storniert": "secondary",
            "pending": "info",
            "confirmed": "success",
            "rejected": "danger",
            "waitlisted": "warning",
        }
        return colors.get(self.status, "secondary")


from app.models.event import Event  # noqa: E402
from app.models.company import ContactPerson, Company  # noqa: E402
