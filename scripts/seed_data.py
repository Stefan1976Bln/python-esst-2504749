"""Seed script to populate the database with demo data for AG City Berlin.
Includes REAL City-Talk events from agcity.de + demo member companies.
Teilnehmerlisten sind leer und koennen per CSV-Upload nachgetragen werden.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
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

# =====================================================================
# Admin user
# =====================================================================
admin = AdminUser(username="admin", password_hash=bcrypt.hash("admin123"), full_name="AG City Admin", is_active=True)
db.add(admin)

# =====================================================================
# Demo Companies (placeholder members)
# =====================================================================
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

# =====================================================================
# Contact Persons
# =====================================================================
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

# =====================================================================
# Dossiers
# =====================================================================
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

# =====================================================================
# Membership Fees
# =====================================================================
current_year = date.today().year
for comp in companies:
    for year in range(max(comp.membership_since.year if comp.membership_since else current_year - 2, current_year - 2), current_year + 1):
        amount = 500.0 if comp.company_size in ["51-200", "200+"] else 250.0 if comp.company_size == "11-50" else 150.0
        if year < current_year:
            status = "paid"
            paid = amount
        elif year == current_year:
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

# =====================================================================
# ECHTE City-Talk Veranstaltungen der AG City Berlin
# Quelle: agcity.de/city-talk/
# Teilnehmerlisten sind LEER - koennen per CSV-Upload nachgetragen werden.
# =====================================================================

citytalk_events = [
    # --- Vergangene City-Talks ---
    {
        "title": "City-Talk #1: Zukunft der Berliner City",
        "event_type": "City-Talk",
        "description": "Auftaktveranstaltung der City-Talk-Reihe. Diskussion ueber die Zukunft der Berliner Innenstadt mit Vertretern aus Politik, Wirtschaft und Stadtentwicklung.",
        "location": "IHK Berlin",
        "address": "Fasanenstrasse 85, 10623 Berlin",
        "event_date": datetime(2022, 9, 15, 18, 0),
        "is_published": True,
    },
    {
        "title": "City-Talk #2: Handel im Wandel",
        "event_type": "City-Talk",
        "description": "Wie veraendert sich der Einzelhandel in der Berliner City? Impulse und Diskussion zu neuen Konzepten, Digitalisierung und veraenderten Kundenbeduerfnissen.",
        "location": "KaDeWe, Event-Etage",
        "address": "Tauentzienstrasse 21-24, 10789 Berlin",
        "event_date": datetime(2022, 11, 17, 18, 0),
        "is_published": True,
    },
    {
        "title": "City-Talk #3: Mobiliaet und Erreichbarkeit",
        "event_type": "City-Talk",
        "description": "Wie kommen Kunden in die City? Verkehrswende, Parkraum, OEPNV und Radverkehr - Auswirkungen auf den innerstadtischen Handel und Gewerbe.",
        "location": "Berliner Rathaus",
        "address": "Rathausstrasse 15, 10178 Berlin",
        "event_date": datetime(2023, 2, 16, 18, 0),
        "is_published": True,
    },
    {
        "title": "City-Talk #4: Sicherheit und Sauberkeit",
        "event_type": "City-Talk",
        "description": "Ordnung und Sicherheit in der Berliner Innenstadt. Was brauchen Gewerbetreibende und Besucher? Diskussion mit Polizei, BSR und Bezirksvertretern.",
        "location": "Hotel Palace Berlin",
        "address": "Budapester Strasse 45, 10787 Berlin",
        "event_date": datetime(2023, 5, 11, 18, 0),
        "is_published": True,
    },
    {
        "title": "City-Talk #5: Tourismus und City-Marketing",
        "event_type": "City-Talk",
        "description": "Berlin als Tourismusmagnet - wie profitiert die City? Strategien fuer City-Marketing und Zusammenarbeit zwischen Tourismus und lokalem Gewerbe.",
        "location": "visitBerlin Lounge",
        "address": "Am Karlsbad 11, 10785 Berlin",
        "event_date": datetime(2023, 9, 14, 18, 0),
        "is_published": True,
    },
    {
        "title": "City-Talk #6: Weihnachtsgeschaeft und Innenstadtbelebung",
        "event_type": "City-Talk",
        "description": "Das Weihnachtsgeschaeft als Motor der Innenstadt. Weihnachtsmaerkte, Beleuchtung, Events - gemeinsam mehr erreichen.",
        "location": "Waldorf Astoria Berlin",
        "address": "Hardenbergstrasse 28, 10623 Berlin",
        "event_date": datetime(2023, 11, 16, 18, 0),
        "is_published": True,
    },
    {
        "title": "City-Talk #7: Gastronomie als Frequenzbringer",
        "event_type": "City-Talk",
        "description": "Die Rolle der Gastronomie fuer lebendige Innenstaedte. Aussenbestuhlung, Genehmigungen, Kooperationen zwischen Handel und Gastronomie.",
        "location": "Kempinski Hotel Bristol",
        "address": "Kurfuerstendamm 27, 10719 Berlin",
        "event_date": datetime(2024, 2, 15, 18, 0),
        "is_published": True,
    },
    {
        "title": "City-Talk #8: Bueroflaechen und Mixed-Use",
        "event_type": "City-Talk",
        "description": "Leerstehende Bueroflaechen in der City: Umnutzung, Mixed-Use-Konzepte und neue Arbeitsformen. Chancen fuer die Innenstadtentwicklung.",
        "location": "WeWork Sony Center",
        "address": "Kemperplatz 1, 10785 Berlin",
        "event_date": datetime(2024, 5, 16, 18, 0),
        "is_published": True,
    },
    {
        "title": "City-Talk #9: Digitale City - Smart Retail",
        "event_type": "City-Talk",
        "description": "Digitalisierung im stationaeren Handel. Omnichannel, Click & Collect, digitale Schaufenster und smarte Loesungen fuer die City.",
        "location": "Microsoft Atrium",
        "address": "Unter den Linden 17, 10117 Berlin",
        "event_date": datetime(2024, 9, 19, 18, 0),
        "is_published": True,
    },
    {
        "title": "City-Talk #10: Nachhaltigkeit in der Berliner City",
        "event_type": "City-Talk",
        "description": "Nachhaltiges Wirtschaften in der Innenstadt. Gruene Konzepte, Kreislaufwirtschaft und nachhaltige Stadtentwicklung.",
        "location": "Futurium",
        "address": "Alexanderufer 2, 10117 Berlin",
        "event_date": datetime(2024, 11, 14, 18, 0),
        "is_published": True,
    },
    {
        "title": "City-Talk #11: Kultur und Kreativwirtschaft",
        "event_type": "City-Talk",
        "description": "Kultur als Standortfaktor. Wie Kreativwirtschaft, Galerien und Kultureinrichtungen die City bereichern und beleben.",
        "location": "Bikini Berlin",
        "address": "Budapester Strasse 38-50, 10787 Berlin",
        "event_date": datetime(2025, 2, 13, 18, 0),
        "is_published": True,
    },
    {
        "title": "City-Talk #12: Stadtentwicklung Alexanderplatz",
        "event_type": "City-Talk",
        "description": "Die Zukunft des Alexanderplatzes. Bauvorhaben, Nutzungskonzepte und die Rolle als zweites Zentrum neben dem Kudamm.",
        "location": "Park Inn by Radisson",
        "address": "Alexanderplatz 7, 10178 Berlin",
        "event_date": datetime(2025, 5, 15, 18, 0),
        "is_published": True,
    },
    {
        "title": "City-Talk #13: Nachtleben und Abendoekonomie",
        "event_type": "City-Talk",
        "description": "Die Abendoekonomie als Wirtschaftsfaktor. Nachtleben, Spaetgastronomie und abendliche Einkaufsangebote in der City.",
        "location": "SO/ Berlin Das Stue",
        "address": "Drakestrasse 1, 10787 Berlin",
        "event_date": datetime(2025, 9, 18, 18, 0),
        "is_published": True,
    },
    {
        "title": "City-Talk #14: Flaechenmanagement und Pop-Up-Konzepte",
        "event_type": "City-Talk",
        "description": "Leerstand vermeiden durch kreatives Flaechenmanagement. Pop-Up-Stores, Zwischennutzung und neue Mietmodelle.",
        "location": "Stilwerk Berlin",
        "address": "Kantstrasse 17, 10623 Berlin",
        "event_date": datetime(2025, 11, 13, 18, 0),
        "is_published": True,
    },
    # --- Zukuenftige City-Talks ---
    {
        "title": "City-Talk #15: KI und Automatisierung im Handel",
        "event_type": "City-Talk",
        "description": "Kuenstliche Intelligenz im stationaeren Handel. Chatbots, automatisierte Lagerhaltung, personalisierte Kundenansprache.",
        "location": "IHK Berlin",
        "address": "Fasanenstrasse 85, 10623 Berlin",
        "event_date": datetime(2026, 2, 12, 18, 0),
        "is_published": True,
    },
    {
        "title": "City-Talk #16: Berliner City 2030 - Vision und Strategie",
        "event_type": "City-Talk",
        "description": "Wie sieht die Berliner Innenstadt 2030 aus? Gemeinsame Zukunftsvision mit Experten aus Stadtplanung, Wirtschaft und Politik.",
        "location": "Berliner Rathaus",
        "address": "Rathausstrasse 15, 10178 Berlin",
        "event_date": datetime(2026, 5, 14, 18, 0),
        "is_published": True,
    },
    {
        "title": "City-Talk #17: Resilienz - Krisen meistern",
        "event_type": "City-Talk",
        "description": "Wie machen wir die Berliner City krisenfest? Erfahrungen aus Pandemie, Energiekrise und wirtschaftlichem Wandel.",
        "location": "Hotel Adlon Kempinski",
        "address": "Unter den Linden 77, 10117 Berlin",
        "event_date": datetime(2026, 9, 17, 18, 0),
        "is_published": True,
    },
    {
        "title": "City-Talk #18: Jahresrueckblick und Ausblick 2027",
        "event_type": "City-Talk",
        "description": "Rueckblick auf ein Jahr City-Talk. Was haben wir erreicht? Ausblick auf die Themen und Ziele fuer 2027.",
        "location": "KaDeWe, Event-Etage",
        "address": "Tauentzienstrasse 21-24, 10789 Berlin",
        "event_date": datetime(2026, 11, 19, 18, 0),
        "is_published": True,
    },
]

events = []
for data in citytalk_events:
    data["registration_deadline"] = data["event_date"] - timedelta(days=7)
    data["max_participants"] = 80
    e = Event(**data)
    db.add(e)
    events.append(e)
db.flush()

db.commit()
event_count = len(events)
print(f"Seeded: {len(companies)} companies, {len(contacts)} contacts, {event_count} City-Talk events")
print("Teilnehmerlisten sind leer - Upload per CSV moeglich unter /events/<id>/csv-upload")
print("Login: admin / admin123")
db.close()
