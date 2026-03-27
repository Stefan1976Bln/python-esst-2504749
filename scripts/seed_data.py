"""Seed script for AG City Berlin.
Echte City-Talk Events + echte Mitgliedsdaten (anonymisiert).
Teilnehmerlisten leer - per CSV-Upload nachfuellbar.
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
# ECHTE Mitgliedsunternehmen und Ansprechpartner (aus CRM-Export)
# Nachnamen anonymisiert
# =====================================================================

def _d(s):
    """Parse DD.MM.YYYY date, return None on failure."""
    if not s or not s.strip():
        return None
    try:
        return datetime.strptime(s.strip(), "%d.%m.%Y").date()
    except ValueError:
        return None

# Each entry: (firma, firma2, anrede, titel, vorname, nachname, position,
#              strasse, plz, ort, staat, telefon, direkt, mobil, privat,
#              email, geburtstag, beitrag, branche, crm_id, eintrittsdatum)
members_data = [
    # Privatpersonen (keine Firma)
    (None, None, "Frau", None, "Samar", "lllll", None,
     "Tharandter Strasse 2", "10717", "Berlin", "DEUTSCHLAND",
     None, None, "0173 609 3080", None, "abc@gmx.de", None,
     300, "901 Sonstige: Privatpersonen", 25535, "19.06.2025"),
    (None, None, "Herrn", None, "Gregor", "lllll", None,
     "Muellerstrasse 65", "12623", "Berlin", "DEUTSCHLAND",
     "0160 - 80 66 775", None, "0160 - 80 65 775", None, "bcd@gmx.de", None,
     300, "699 Dienstleistung: Sonstige Dienstleister", 25347, "01.01.2024"),
    (None, None, "Herrn", None, "Bernd", "mmmmm", None,
     "Lindenstrasse 60", "14467", "Potsdam", "DEUTSCHLAND",
     None, None, "0172 620 5642", None, "abc@gmx.de", None,
     300, None, 25689, "10.11.2025"),
    (None, None, None, None, "Dirk", "mmmmm", "Bauplanung",
     "Burgweg 11", "17039", "Neuenkirchen", "DEUTSCHLAND",
     None, None, "0155 68 46 7878", None, "bcd@gmx.de", None,
     300, None, 25761, "04.02.2026"),
    (None, None, "Frau", "Dr.", "Sabine", "rrr", "Aerztin",
     "Uhlandstrasse 29", "10719", "Berlin", "DEUTSCHLAND",
     None, None, None, None, "abc@gmx.de", None,
     300, "602 Dienstleistung: Aerzte, Zahnaerzte, Heilberufe", 25773, "11.03.2026"),
    (None, None, "Frau", None, "Antje", "lllll", None,
     "Buddestrasse 9", "13507", "Berlin", None,
     None, "15118261179", None, None, "bcd@gmx.de", None,
     300, "Dienstleistung", 24244, "09.10.2023"),
    # Firmen
    ("008 Obitz & Grigoriadis GbR", None, "Herrn", None, "Albert", "ooo", "CEO",
     "Bundesallee 19", "10717", "Berlin", "DEUTSCHLAND",
     None, "030 373 00000", None, None, "abc@gmx.de", None,
     600, "609 Dienstleistung: IT, Internet, Telekommunikation", 25635, "20.10.2025"),
    ("25hours Hotel Company Berlin GmbH", None, "Frau", None, "Francesca", "sss", "General Manager",
     "Budapester Strasse 40", "10787", "Berlin", None,
     None, "+49 30 120 221 770", "+176 125 25 312", None, "bcd@gmx.de", "08.02.1966",
     600, "Hotel", 12030, "11.06.2014"),
    ("360 Degree World UG (haftungsbeschraenkt)", None, "Herrn", None, "Andreas", "kkk", "GBDO",
     "Schoenhauser Allee 125", "10437", "Berlin", "DEUTSCHLAND",
     None, "030 374 33 244", "0172 4777 778", None, "abc@gmx.de", None,
     600, "607 Dienstleistung: Freizeit, Kultur, Touristik", 25769, "09.03.2026"),
    ("3B Berlin Premium Hotelservice GmbH", None, "Frau", None, "Petra", "ttt", "Geschaeftsfuehrerin",
     "Turmstrasse 33", "10551", "Berlin", None,
     "030.600 316 6-0", None, None, None, "bcd@gmx.de", None,
     600, "Dienstleistung", 13394, "29.08.2012"),
    ("adidas AG", "adidas Homecourt Store", "Frau", None, "Nicole", "kkk", "Store Manager",
     "Tauentzienstrasse 15", "10789", "Berlin", None,
     None, "030 236 31 944", None, None, "abc@gmx.de", None,
     600, "Handel", 5493, "02.02.2007"),
    ("Aengevelt Immobilien GmbH & Co. KG", None, "Frau", None, "Tina", "ssss", "Niederlassungsleiterin Berlin",
     "Franzoesische Strasse 48", "10117", "Berlin", None,
     "+49 30 20193-130", None, "+49 172 9804-130", None, "bcd@gmx.de", None,
     600, "Immobilien", 20003, "17.08.2017"),
    ("AFC Berlin Adler e.V.", None, "Herrn", None, "Denis", "mmmmm", "Geschaeftsfuehrer / General Manager",
     "Kurt-Schumacher-Damm 207-214", "13405", "Berlin", "DEUTSCHLAND",
     "+49 30 32531606", None, "0170 - 210 48 23", None, "abc@gmx.de", None,
     600, "711 Oeffentliche Organisationen: Vereine", 24405, "25.02.2024"),
]

companies = []
contacts = []
company_map = {}  # name -> Company object

for (firma, firma2, anrede, titel, vorname, nachname, position,
     strasse, plz, ort, staat, telefon, direkt, mobil, privat,
     email, geburtstag, beitrag, branche, crm_id, eintrittsdatum) in members_data:

    # Determine company
    if firma:
        comp_key = firma
    else:
        comp_key = f"Privatperson: {vorname} {nachname}"

    if comp_key not in company_map:
        comp = Company(
            name=comp_key,
            name2=firma2,
            address=strasse,
            postal_code=plz,
            city=ort,
            staat=staat,
            branche=branche,
            beitrag=float(beitrag) if beitrag else None,
            crm_id=crm_id,
            membership_since=_d(eintrittsdatum),
            is_active=True,
        )
        db.add(comp)
        db.flush()
        company_map[comp_key] = comp
        companies.append(comp)

    comp = company_map[comp_key]
    is_first = not any(c.company_id == comp.id for c in contacts)

    cp = ContactPerson(
        company_id=comp.id,
        anrede=anrede,
        titel=titel,
        first_name=vorname.strip() if vorname else "",
        last_name=nachname.strip() if nachname else "",
        position=position,
        email=email,
        phone=telefon,
        phone_direct=direkt,
        phone_mobile=mobil,
        phone_private=privat,
        birthday=_d(geburtstag),
        is_primary=is_first,
        crm_id=crm_id,
    )
    db.add(cp)
    contacts.append(cp)

db.flush()

# =====================================================================
# Membership Fees (basierend auf echtem Beitrag)
# =====================================================================
current_year = date.today().year
for comp in companies:
    start_year = comp.membership_since.year if comp.membership_since else current_year
    for year in range(max(start_year, current_year - 2), current_year + 1):
        amount = comp.beitrag or 300.0
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
    data["is_published"] = True
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
