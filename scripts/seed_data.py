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
# Quelle: Offizielle Liste AG City Berlin
# Teilnehmerlisten sind LEER - koennen per CSV-Upload nachgetragen werden.
# =====================================================================

citytalk_events = [
    # --- 2022 ---
    {"title": "F80 Die Zahn- und Gesichtsspezialisten", "event_type": "City-Talk", "location": "F80 Die Zahn- und Gesichtsspezialisten", "event_date": datetime(2022, 3, 15, 18, 0)},
    {"title": "Parkstrom GmbH", "event_type": "City-Talk", "location": "Parkstrom GmbH", "event_date": datetime(2022, 3, 31, 18, 0)},
    {"title": "50 Jahre Woodstock - Die Ausstellung", "event_type": "City-Talk", "location": "50 Jahre Woodstock - Die Ausstellung", "event_date": datetime(2022, 4, 26, 18, 0)},
    {"title": "Dt. PalliativStiftung | TITANIC Gendarmenmarkt", "event_type": "City-Talk", "location": "TITANIC Gendarmenmarkt", "event_date": datetime(2022, 5, 24, 18, 0)},
    {"title": "Musicalbesuch Ku'damm 56", "event_type": "City-Talk", "location": "Musical Ku'damm 56", "event_date": datetime(2022, 6, 10, 18, 0)},
    {"title": "HUAWEI Flagship Store", "event_type": "City-Talk", "location": "HUAWEI Flagship Store", "event_date": datetime(2022, 7, 5, 18, 0)},
    {"title": "TimeRide", "event_type": "City-Talk", "location": "TimeRide Berlin", "event_date": datetime(2022, 8, 16, 18, 0)},
    {"title": "stilwerk KantGaragen", "event_type": "City-Talk", "location": "stilwerk KantGaragen", "event_date": datetime(2022, 9, 15, 18, 0)},
    {"title": "the burrow", "event_type": "City-Talk", "location": "the burrow", "event_date": datetime(2022, 10, 20, 18, 0)},
    {"title": "Christmas City Talk", "event_type": "City-Talk", "location": "Christmas City Talk", "event_date": datetime(2022, 12, 7, 18, 0)},
    {"title": "City Talk WeihnachtsZauber Gendarmenmarkt", "event_type": "City-Talk", "location": "WeihnachtsZauber Gendarmenmarkt", "event_date": datetime(2022, 12, 20, 18, 0)},
    # --- 2023 ---
    {"title": "KaDeWe", "event_type": "City-Talk", "location": "KaDeWe", "event_date": datetime(2023, 2, 15, 18, 0)},
    {"title": "POP KUDAMM", "event_type": "City-Talk", "location": "POP KUDAMM", "event_date": datetime(2023, 3, 23, 18, 0)},
    {"title": "PanAm Lounge", "event_type": "City-Talk", "location": "PanAm Lounge", "event_date": datetime(2023, 3, 27, 18, 0)},
    {"title": "reproplan Berlin", "event_type": "City-Talk", "location": "reproplan Berlin", "event_date": datetime(2023, 4, 20, 18, 0)},
    {"title": "Ku64", "event_type": "City-Talk", "location": "Ku64", "event_date": datetime(2023, 5, 4, 18, 0)},
    {"title": "Schmelzwerk", "event_type": "City-Talk", "location": "Schmelzwerk", "event_date": datetime(2023, 6, 26, 18, 0)},
    {"title": "DINNEBIER Premium-Cars", "event_type": "City-Talk", "location": "DINNEBIER Premium-Cars", "event_date": datetime(2023, 7, 5, 18, 0)},
    {"title": "Cold War Museum", "event_type": "City-Talk", "location": "Cold War Museum", "event_date": datetime(2023, 8, 22, 18, 0)},
    {"title": "Dallmayr Catering | Drive Volkswagen Group Forum", "event_type": "City-Talk", "location": "Drive Volkswagen Group Forum", "event_date": datetime(2023, 8, 30, 18, 0)},
    {"title": "City Talk NIO House Berlin | MSC - MobileSpeedCircus", "event_type": "City-Talk", "location": "NIO House Berlin", "event_date": datetime(2023, 9, 14, 18, 0)},
    {"title": "City Talk der Berliner Krebsgesellschaft e.V.", "event_type": "City-Talk", "location": "Berliner Krebsgesellschaft e.V.", "event_date": datetime(2023, 9, 26, 18, 0)},
    {"title": "City Talk bei GODELMANN im BIKINI BERLIN", "event_type": "City-Talk", "location": "GODELMANN im BIKINI BERLIN", "event_date": datetime(2023, 10, 5, 18, 0)},
    {"title": "Branchen-City Talk im Kabarett Theater Die Stachelschweine", "event_type": "City-Talk", "location": "Kabarett Theater Die Stachelschweine", "event_date": datetime(2023, 11, 17, 18, 0)},
    {"title": "City Talk WeihnachtsZauber Gendarmenmarkt", "event_type": "City-Talk", "location": "WeihnachtsZauber Gendarmenmarkt", "event_date": datetime(2023, 12, 5, 18, 0)},
    {"title": "Christmas City Talk Hirschstube Breitscheidplatz", "event_type": "City-Talk", "location": "Hirschstube Breitscheidplatz", "event_date": datetime(2023, 12, 14, 18, 0)},
    # --- 2024 ---
    {"title": "City Talk in der Ausstellung Das Romanische Cafe", "event_type": "City-Talk", "location": "Ausstellung Das Romanische Cafe", "event_date": datetime(2024, 1, 31, 18, 0)},
    {"title": "City Talk im Johnson Fitness & Wellness Store Berlin-Steglitz", "event_type": "City-Talk", "location": "Johnson Fitness & Wellness Store Berlin-Steglitz", "event_date": datetime(2024, 2, 15, 18, 0)},
    {"title": "City Talk im RTL Audio Center Berlin", "event_type": "City-Talk", "location": "RTL Audio Center Berlin", "event_date": datetime(2024, 4, 23, 18, 0)},
    {"title": "Hotel am Steinplatz", "event_type": "City-Talk", "location": "Hotel am Steinplatz", "event_date": datetime(2024, 5, 13, 18, 0)},
    {"title": "City Talk bei BMW Nefzger", "event_type": "City-Talk", "location": "BMW Nefzger", "event_date": datetime(2024, 5, 30, 18, 0)},
    {"title": "City Talk IFA 100 The Exhibition", "event_type": "City-Talk", "location": "IFA 100 The Exhibition", "event_date": datetime(2024, 7, 10, 18, 0)},
    {"title": "City Talk der Reederei Stern + Kreis", "event_type": "City-Talk", "location": "Reederei Stern + Kreis", "event_date": datetime(2024, 8, 14, 18, 0)},
    {"title": "City Talk Kudamm 59 im Stage Theater des Westens", "event_type": "City-Talk", "location": "Stage Theater des Westens", "event_date": datetime(2024, 9, 4, 18, 0)},
    {"title": "City Talk im Deutschlandmuseum", "event_type": "City-Talk", "location": "Deutschlandmuseum", "event_date": datetime(2024, 9, 10, 18, 0)},
    {"title": "City Talk im Living Berlin", "event_type": "City-Talk", "location": "Living Berlin", "event_date": datetime(2024, 10, 10, 18, 0)},
    {"title": "City Talk WeihnachtsZauber Gendarmenmarkt", "event_type": "City-Talk", "location": "WeihnachtsZauber Gendarmenmarkt", "event_date": datetime(2024, 12, 3, 18, 0)},
    {"title": "Christmas City Talk Hirschstube Breitscheidplatz", "event_type": "City-Talk", "location": "Hirschstube Breitscheidplatz", "event_date": datetime(2024, 12, 10, 18, 0)},
    # --- 2025 ---
    {"title": "City Talk im Johnson Fitness & Wellness Store", "event_type": "City-Talk", "location": "Johnson Fitness & Wellness Store", "event_date": datetime(2025, 1, 23, 18, 0)},
    {"title": "City Talk im Vivont Berlin Eventlocation", "event_type": "City-Talk", "location": "Vivont Berlin Eventlocation", "event_date": datetime(2025, 2, 13, 18, 0)},
    {"title": "City Talk des Wirtschaftsrat des 1. FC Union", "event_type": "City-Talk", "location": "1. FC Union Berlin", "event_date": datetime(2025, 3, 6, 18, 0)},
    {"title": "City Talk bei der Audi Berlin GmbH", "event_type": "City-Talk", "location": "Audi Berlin GmbH", "event_date": datetime(2025, 3, 13, 18, 0)},
    {"title": "City Talk Kamingespraeche im Estrel", "event_type": "City-Talk", "location": "Estrel Berlin", "event_date": datetime(2025, 5, 6, 18, 0)},
    {"title": "City Talk im Samurai Museum Berlin", "event_type": "City-Talk", "location": "Samurai Museum Berlin", "event_date": datetime(2025, 5, 13, 18, 0)},
    {"title": "AG City Stammtisch im Berlin Capital Club", "event_type": "Stammtisch", "location": "Berlin Capital Club", "event_date": datetime(2025, 6, 4, 18, 0)},
    {"title": "City Talk im Chamaeleon - Kultur, Geschichte und Begegnung in den Hackeschen Hoefen", "event_type": "City-Talk", "location": "Chamaeleon Theater, Hackesche Hoefe", "event_date": datetime(2025, 6, 11, 18, 0)},
    {"title": "City Talk im Artverse.Underground", "event_type": "City-Talk", "location": "Artverse.Underground", "event_date": datetime(2025, 7, 31, 18, 0)},
    {"title": "City Talk - Nicoleta Gallery Berlin", "event_type": "City-Talk", "location": "Nicoleta Gallery Berlin", "event_date": datetime(2025, 9, 16, 18, 0)},
    {"title": "City Talk - HYGH AG", "event_type": "City-Talk", "location": "HYGH AG", "event_date": datetime(2025, 10, 23, 18, 0)},
    {"title": "City Talk - Weinheuer GmbH", "event_type": "City-Talk", "location": "Weinheuer GmbH", "event_date": datetime(2025, 11, 26, 18, 0)},
    {"title": "City Talk - WeihnachtsZauber Gendarmenmarkt", "event_type": "City-Talk", "location": "WeihnachtsZauber Gendarmenmarkt", "event_date": datetime(2025, 12, 3, 18, 0)},
    {"title": "City Talk Hirschstube", "event_type": "City-Talk", "location": "Hirschstube", "event_date": datetime(2025, 12, 9, 18, 0)},
    # --- 2026 ---
    {"title": "City Talk Masumi Space", "event_type": "City-Talk", "location": "Masumi Space", "event_date": datetime(2026, 1, 15, 18, 0)},
    {"title": "City Talk KaDeWe Berlin", "event_type": "City-Talk", "location": "KaDeWe Berlin", "event_date": datetime(2026, 2, 12, 18, 0)},
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
