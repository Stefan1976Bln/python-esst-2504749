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
    motivation: Mapped[str | None] = mapped_column(Text)  # "Why do you want to attend?"

    # Status workflow: pending -> confirmed/rejected/waitlisted
    status: Mapped[str] = mapped_column(String(20), default="pending")
    # Attendance: null -> attended / no_show
    attendance: Mapped[str | None] = mapped_column(String(20))
    admin_notes: Mapped[str | None] = mapped_column(Text)

    # AI fields
    ai_suitability_score: Mapped[float | None] = mapped_column(Float)
    ai_suitability_reason: Mapped[str | None] = mapped_column(Text)
    ai_reliability_score: Mapped[float | None] = mapped_column(Float)

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
    def combined_ai_score(self) -> float | None:
        scores = [s for s in [self.ai_suitability_score, self.ai_reliability_score] if s is not None]
        if not scores:
            return None
        return sum(scores) / len(scores)


from app.models.event import Event  # noqa: E402
from app.models.company import ContactPerson, Company  # noqa: E402
