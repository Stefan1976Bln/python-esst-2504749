import uuid
from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    event_type: Mapped[str | None] = mapped_column(String(50))  # workshop, networking, seminar, gala
    description: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(255))
    address: Mapped[str | None] = mapped_column(Text)
    event_date: Mapped[datetime] = mapped_column(DateTime)
    event_end_date: Mapped[datetime | None] = mapped_column(DateTime)
    max_participants: Mapped[int | None] = mapped_column(Integer)
    registration_deadline: Mapped[datetime | None] = mapped_column(DateTime)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    public_token: Mapped[str] = mapped_column(String(64), unique=True, default=lambda: str(uuid.uuid4()))
    ai_summary: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    images: Mapped[list["EventImage"]] = relationship(back_populates="event", cascade="all, delete-orphan")
    registrations: Mapped[list["EventRegistration"]] = relationship(back_populates="event", cascade="all, delete-orphan")

    @property
    def confirmed_count(self) -> int:
        return sum(1 for r in self.registrations if r.status == "confirmed")

    @property
    def pending_count(self) -> int:
        return sum(1 for r in self.registrations if r.status == "pending")

    @property
    def is_past(self) -> bool:
        return self.event_date < datetime.utcnow()


class EventImage(Base):
    __tablename__ = "event_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    file_path: Mapped[str] = mapped_column(String(500))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    caption: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    event: Mapped["Event"] = relationship(back_populates="images")


from app.models.registration import EventRegistration  # noqa: E402
