"""Seed script to populate the database with demo data for AG City."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, datetime, timedelta
from app.database import SessionLocal, engine, Base
from app.models.company import Company, ContactPerson, Dossier
from app.models.membership import MembershipFee, PaymentRecord
from app.models.event import Event
from app.models.registration import EventRegistration
from app.models.user import AdminUser
from passlib.hash import bcrypt

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Clear existing data
for table in reversed(Base.metadata.sorted_tables):
    db.execute(table.delete())
db.commit()

print("Seeding demo data...")

# Admin user
admin = AdminUser(username="admin", password_hash=bcrypt.hash("admin123"), full_name="AG City Admin", is_active=True)
db.add(admin)

# Companies
companies_data = [
    {"name": "Mueller & Partner Rechtsanwaelte", "branche": "Rechtsberatung", "city": "Berlin", "postal_code": "10115",
     "address": "Friedrichstrasse 42", "phone": "+49 30 12345678", "email": "info@mueller-partner.de",
     "website": "www.mueller-partner.de", "company_size": "11-50", "membership_since": date(2020, 1, 15)},
    {"name": "TechVision GmbH", "branche": "IT & Software", "city": "Berlin", "postal_code": "10178",
     "address": "Alexanderplatz 7", "phone": "+49 30 98765432", "email": "kontakt@techvision.de",
     "website": "www.techvision.de", "company_size": "51-200", "membership_since": date(2019, 6, 1)},
    {"name": "Cafe Sonnenschein", "branche": "Gastronomie", "city": "Berlin", "postal_code": "10243",
     "address": "Karl-Marx-Allee 15", "phone": "+49 30 55544433", "email": "hallo@cafe-sonnenschein.de",
     "website": "www.cafe-sonnenschein.de", "company_size": "1-10", "membership_since": date(2021, 3, 10)},
    {"name": "Berliner Modehaus Schmidt", "branche": "Einzelhandel / Mode", "city": "Berlin", "postal_code": "10719",
     "address": "Kurfuerstendamm 88", "phone": "+49 30 77788899", "email": "info@modehaus-schmidt.de",
     "website": "www.modehaus-schmidt.de", "company_size": "11-50", "membership_since": date(2018, 9, 20)},
    {"name": "Gruene Energie Berlin AG", "branche": "Erneuerbare Energien", "city": "Berlin", "postal_code": "10557",
     "address": "Invalidenstrasse 31", "phone": "+49 30 33322211", "email": "info@gruene-energie-berlin.de",
     "website": "www.gruene-energie-berlin.de", "company_size": "51-200", "membership_since": date(2022, 1, 5)},
    {"name": "Immobilien Krause KG", "branche": "Immobilien", "city": "Berlin", "postal_code": "10785",
     "address": "Potsdamer Platz 3", "phone": "+49 30 44455566", "email": "kontakt@krause-immobilien.de",
     "website": "www.krause-immobilien.de", "company_size": "11-50", "membership_since": date(2017, 5, 12)},
    {"name": "Buchhandlung am Kiez", "branche": "Einzelhandel / Buecher", "city": "Berlin", "postal_code": "10999",
     "address": "Oranienstrasse 22", "phone": "+49 30 11122233", "email": "info@buchhandlung-kiez.de",
     "website": "", "company_size": "1-10", "membership_since": date(2023, 2, 1)},
    {"name": "Dr. Weber Zahnarztpraxis", "branche": "Gesundheit", "city": "Berlin", "postal_code": "10629",
     "address": "Savignyplatz 5", "phone": "+49 30 66677788", "email": "praxis@dr-weber.de",
     "website": "www.dr-weber-zahnarzt.de", "company_size": "1-10", "membership_since": date(2020, 8, 15)},
    {"name": "Kreativ Agentur Funke", "branche": "Marketing & Werbung", "city": "Berlin", "postal_code": "10965",
     "address": "Bergmannstrasse 19", "phone": "+49 30 88899900", "email": "hello@funke-kreativ.de",
     "website": "www.funke-kreativ.de", "company_size": "11-50", "membership_since": date(2021, 11, 8)},
    {"name": "Handwerksbetrieb Hoffmann", "branche": "Handwerk", "city": "Berlin", "postal_code": "12049",
     "address": "Hermannstrasse 40", "phone": "+49 30 22233344", "email": "info@hoffmann-handwerk.de",
     "website": "", "company_size": "1-10", "membership_since": date(2019, 4, 20)},
]

companies = []
for data in companies_data:
    c = Company(**data, is_active=True)
    db.add(c)
    companies.append(c)
db.flush()

# Contact Persons
contacts_data = [
    (0, "Thomas", "Mueller", "Geschaeftsfuehrer", "t.mueller@mueller-partner.de", "+49 170 1111111", True),
    (0, "Anna", "Schneider", "Assistenz", "a.schneider@mueller-partner.de", "+49 170 1111112", False),
    (1, "Stefan", "Wagner", "CTO", "s.wagner@techvision.de", "+49 171 2222222", True),
    (1, "Lisa", "Becker", "Marketing", "l.becker@techvision.de", "+49 171 2222223", False),
    (2, "Maria", "Klein", "Inhaberin", "m.klein@cafe-sonnenschein.de", "+49 172 3333333", True),
    (3, "Heinrich", "Schmidt", "Inhaber", "h.schmidt@modehaus-schmidt.de", "+49 173 4444444", True),
    (3, "Katrin", "Schmidt", "Einkauf", "k.schmidt@modehaus-schmidt.de", "+49 173 4444445", False),
    (4, "Dr. Frank", "Neumann", "Vorstand", "f.neumann@gruene-energie-berlin.de", "+49 174 5555555", True),
    (5, "Michael", "Krause", "Geschaeftsfuehrer", "m.krause@krause-immobilien.de", "+49 175 6666666", True),
    (6, "Julia", "Braun", "Inhaberin", "j.braun@buchhandlung-kiez.de", "+49 176 7777777", True),
    (7, "Dr. Peter", "Weber", "Praxisinhaber", "p.weber@dr-weber.de", "+49 177 8888888", True),
    (8, "Carla", "Funke", "Creative Director", "c.funke@funke-kreativ.de", "+49 178 9999999", True),
    (8, "Maximilian", "Koch", "Projektmanager", "m.koch@funke-kreativ.de", "+49 178 9999998", False),
    (9, "Hans", "Hoffmann", "Meister", "h.hoffmann@hoffmann-handwerk.de", "+49 179 0000000", True),
]

contacts = []
for comp_idx, first, last, role, email, phone, primary in contacts_data:
    cp = ContactPerson(
        company_id=companies[comp_idx].id, first_name=first, last_name=last,
        role=role, email=email, phone=phone, is_primary=primary,
    )
    db.add(cp)
    contacts.append(cp)
db.flush()

# Dossiers
dossiers_data = [
    ("company", companies[0].id, "Erstgespraech", "Herr Mueller ist sehr interessiert an Networking-Events. Kanzlei hat 25 Mitarbeiter und sucht Mandanten im Mittelstand.", "Admin"),
    ("company", companies[1].id, "Technologie-Partner", "TechVision bietet Cloud-Loesungen fuer KMU an. Koennten als Sponsor fuer Tech-Events gewonnen werden.", "Admin"),
    ("company", companies[3].id, "Traditionsbetrieb", "Seit 1955 am Ku'damm. Herr Schmidt legt Wert auf persoenliche Kontakte. Sehr aktives Mitglied.", "Admin"),
    ("company", companies[4].id, "Neues Mitglied", "Schnell wachsendes Unternehmen. Interesse an Nachhaltigkeit und gruener Wirtschaft.", "Admin"),
    ("contact", contacts[0].id, "Networking-Typ", "Herr Mueller kommt zu fast jeder Veranstaltung und bringt oft Gaeste mit.", "Admin"),
    ("contact", contacts[2].id, "Tech-Experte", "Stefan Wagner hat auf dem letzten Workshop einen Vortrag zu KI gehalten. Sehr guter Speaker.", "Admin"),
]

for entity_type, entity_id, title, content, author in dossiers_data:
    d = Dossier(entity_type=entity_type, entity_id=entity_id, title=title, content=content, author=author)
    db.add(d)

# Membership Fees
current_year = date.today().year
for comp in companies:
    for year in range(max(comp.membership_since.year if comp.membership_since else current_year - 2, current_year - 2), current_year + 1):
        amount = 500.0 if comp.company_size in ["51-200", "200+"] else 250.0 if comp.company_size == "11-50" else 150.0
        if year < current_year:
            status = "paid"
            paid = amount
        elif year == current_year:
            import random
            if random.random() > 0.3:
                status = "paid"
                paid = amount
            else:
                status = "outstanding"
                paid = 0
        else:
            status = "outstanding"
            paid = 0

        fee = MembershipFee(
            company_id=comp.id, year=year, amount_due=amount, amount_paid=paid,
            status=status, due_date=date(year, 1, 31),
        )
        db.add(fee)
        db.flush()

        if paid > 0:
            payment = PaymentRecord(
                fee_id=fee.id, amount=paid, payment_date=date(year, 1, 15),
                payment_method="bank_transfer", reference=f"BEITRAG-{year}-{comp.id}",
            )
            db.add(payment)

# Events
now = datetime.utcnow()
events_data = [
    {"title": "Fruehlings-Networking Abend", "event_type": "Networking", "description": "Lockeres Networking bei Fingerfood und Getraenken. Lernen Sie andere Unternehmer aus der Nachbarschaft kennen.", "location": "Cafe Sonnenschein", "address": "Karl-Marx-Allee 15, Berlin", "event_date": now - timedelta(days=60), "max_participants": 40, "is_published": True},
    {"title": "Workshop: Digitalisierung im Einzelhandel", "event_type": "Workshop", "description": "Praktische Tipps zur Digitalisierung Ihres Geschaefts: Online-Praesenz, Social Media, E-Commerce Grundlagen.", "location": "TechVision Office", "address": "Alexanderplatz 7, Berlin", "event_date": now - timedelta(days=30), "max_participants": 25, "is_published": True},
    {"title": "Sommer-Gala 2026", "event_type": "Gala", "description": "Die jaehrliche AG City Sommer-Gala mit Auszeichnung der engagiertesten Mitglieder, Live-Musik und 3-Gaenge-Menue.", "location": "Hotel Adlon", "address": "Unter den Linden 77, Berlin", "event_date": now + timedelta(days=45), "max_participants": 100, "is_published": True},
    {"title": "Seminar: Nachhaltigkeit als Geschaeftsmodell", "event_type": "Seminar", "description": "Wie Sie Ihr Unternehmen nachhaltig aufstellen und davon profitieren. Mit Gastreferent Dr. Frank Neumann.", "location": "Gruene Energie Berlin HQ", "address": "Invalidenstrasse 31, Berlin", "event_date": now + timedelta(days=20), "max_participants": 30, "is_published": True},
    {"title": "Herbst-Networking im Kiez", "event_type": "Networking", "description": "Entspanntes Treffen in der Buchhandlung am Kiez mit Lesung und anschliessendem Networking.", "location": "Buchhandlung am Kiez", "address": "Oranienstrasse 22, Berlin", "event_date": now + timedelta(days=90), "max_participants": 35, "is_published": True},
    {"title": "KI-Workshop fuer Einsteiger", "event_type": "Workshop", "description": "Grundlagen der Kuenstlichen Intelligenz fuer Unternehmer. Praktische Anwendungsbeispiele und Hands-on Uebungen.", "location": "TechVision Office", "address": "Alexanderplatz 7, Berlin", "event_date": now + timedelta(days=60), "max_participants": 20, "is_published": True},
]

events = []
for data in events_data:
    data["registration_deadline"] = data["event_date"] - timedelta(days=7)
    e = Event(**data)
    db.add(e)
    events.append(e)
db.flush()

# Registrations for past events
import random

# Past event 1 - networking
for i, contact in enumerate(contacts[:8]):
    comp = companies[contacts_data[i][0]] if i < len(contacts_data) else None
    reg = EventRegistration(
        event_id=events[0].id, contact_person_id=contact.id,
        company_id=comp.id if comp else None,
        first_name=contact.first_name, last_name=contact.last_name,
        email=contact.email, phone=contact.phone,
        organization=comp.name if comp else "", branche=comp.branche if comp else "",
        is_member=True, status="confirmed",
        attendance=random.choice(["attended", "attended", "attended", "no_show"]),
    )
    db.add(reg)

# Past event 2 - workshop
for contact in contacts[1:6]:
    reg = EventRegistration(
        event_id=events[1].id, contact_person_id=contact.id,
        first_name=contact.first_name, last_name=contact.last_name,
        email=contact.email, organization="", branche="",
        is_member=True, status="confirmed",
        attendance=random.choice(["attended", "attended", "no_show"]),
    )
    db.add(reg)

# Future event 3 - Gala (many registrations, some pending)
for contact in contacts:
    status = random.choice(["pending", "pending", "confirmed", "confirmed", "confirmed"])
    reg = EventRegistration(
        event_id=events[2].id, contact_person_id=contact.id,
        first_name=contact.first_name, last_name=contact.last_name,
        email=contact.email, phone=contact.phone,
        organization="", branche="", is_member=True,
        status=status, motivation="Moechte gerne am Netzwerken teilnehmen und neue Kontakte knuepfen.",
    )
    db.add(reg)

# Non-member registrations for Gala
non_members = [
    ("Sandra", "Fischer", "s.fischer@example.com", "Fischers Blumenladen", "Einzelhandel / Floristik"),
    ("Bernd", "Hartmann", "b.hartmann@example.com", "Hartmann Consulting", "Beratung"),
    ("Yvonne", "Schreiber", "y.schreiber@example.com", "Schreiber Design", "Design"),
]
for first, last, email, org, branche in non_members:
    reg = EventRegistration(
        event_id=events[2].id,
        first_name=first, last_name=last, email=email,
        organization=org, branche=branche, is_member=False,
        status="pending", motivation="Interesse an der AG City und moeglicher Mitgliedschaft.",
    )
    db.add(reg)

# Future event 4 - Seminar
for contact in [contacts[2], contacts[7], contacts[11], contacts[4]]:
    reg = EventRegistration(
        event_id=events[3].id, contact_person_id=contact.id,
        first_name=contact.first_name, last_name=contact.last_name,
        email=contact.email, is_member=True, status="pending",
        organization="", branche="",
        motivation="Thema Nachhaltigkeit ist fuer unser Unternehmen sehr relevant.",
    )
    db.add(reg)

db.commit()
print(f"Seeded: {len(companies)} companies, {len(contacts)} contacts, {len(events)} events")
print("Login: admin / admin123")
db.close()
