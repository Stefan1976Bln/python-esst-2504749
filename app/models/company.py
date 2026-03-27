from datetime import datetime, date
from sqlalchemy import String, Text, Boolean, Date, DateTime, ForeignKey, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    name2: Mapped[str | None] = mapped_column(String(255))  # Firma2
    name3: Mapped[str | None] = mapped_column(String(255))  # Firma3
    address: Mapped[str | None] = mapped_column(Text)
    postal_code: Mapped[str | None] = mapped_column(String(20))
    city: Mapped[str | None] = mapped_column(String(100))
    staat: Mapped[str | None] = mapped_column(String(100))  # Land/Staat
    phone: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(255))
    website: Mapped[str | None] = mapped_column(String(255))
    branche: Mapped[str | None] = mapped_column(String(255))
    company_size: Mapped[str | None] = mapped_column(String(50))
    membership_since: Mapped[date | None] = mapped_column(Date)  # Eintrittsdatum
    membership_end: Mapped[date | None] = mapped_column(Date)  # Austrittsdatum
    beitrag: Mapped[float | None] = mapped_column(Float)  # Beitrag in EUR
    rechnungstext: Mapped[str | None] = mapped_column(Text)
    crm_id: Mapped[int | None] = mapped_column(Integer, unique=True)  # ID aus CRM-Export
    frei1: Mapped[str | None] = mapped_column(String(255))  # Freifeld 1
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    contacts: Mapped[list["ContactPerson"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    dossiers: Mapped[list["Dossier"]] = relationship(
        back_populates="company",
        primaryjoin="and_(Dossier.entity_type=='company', foreign(Dossier.entity_id)==Company.id)",
        viewonly=True,
    )
    fees: Mapped[list["MembershipFee"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    registrations: Mapped[list["EventRegistration"]] = relationship(back_populates="company")

    @property
    def display_name(self) -> str:
        parts = [self.name]
        if self.name2:
            parts.append(self.name2)
        if self.name3:
            parts.append(self.name3)
        return " - ".join(parts)

    @property
    def outstanding_fees(self) -> float:
        return sum(f.amount_due - f.amount_paid for f in self.fees if f.status != "paid")


class ContactPerson(Base):
    __tablename__ = "contact_persons"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int | None] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"))
    anrede: Mapped[str | None] = mapped_column(String(20))  # Herrn, Frau
    titel: Mapped[str | None] = mapped_column(String(50))  # Dr., Prof.
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    position: Mapped[str | None] = mapped_column(String(200))  # Position/Funktion
    abteilung: Mapped[str | None] = mapped_column(String(100))  # Abteilung
    role: Mapped[str | None] = mapped_column(String(100))  # legacy: kurze Rolle
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))  # Zentrale/Haupt
    phone_direct: Mapped[str | None] = mapped_column(String(50))  # Durchwahl
    phone_mobile: Mapped[str | None] = mapped_column(String(50))  # Mobil
    phone_private: Mapped[str | None] = mapped_column(String(50))  # Privat
    birthday: Mapped[date | None] = mapped_column(Date)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    crm_id: Mapped[int | None] = mapped_column(Integer)  # ID aus CRM
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    company: Mapped["Company | None"] = relationship(back_populates="contacts")
    registrations: Mapped[list["EventRegistration"]] = relationship(back_populates="contact_person")

    @property
    def full_name(self) -> str:
        parts = []
        if self.titel:
            parts.append(self.titel)
        parts.append(self.first_name)
        parts.append(self.last_name)
        return " ".join(parts)

    @property
    def formal_name(self) -> str:
        parts = []
        if self.anrede:
            parts.append(self.anrede)
        if self.titel:
            parts.append(self.titel)
        parts.append(self.first_name)
        parts.append(self.last_name)
        return " ".join(parts)


class Dossier(Base):
    __tablename__ = "dossiers"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(20))  # "company" or "contact"
    entity_id: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    author: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company: Mapped["Company | None"] = relationship(
        back_populates="dossiers",
        primaryjoin="and_(Dossier.entity_type=='company', foreign(Dossier.entity_id)==Company.id)",
        viewonly=True,
    )


# Import here to avoid circular imports
from app.models.membership import MembershipFee  # noqa: E402
from app.models.registration import EventRegistration  # noqa: E402
