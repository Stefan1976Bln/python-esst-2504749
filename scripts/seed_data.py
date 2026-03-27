"""Seed script for AG City Berlin.
Erstellt nur Admin-User und echte City-Talk Events.
Unternehmen/Ansprechpartner werden per CSV-Import hinzugefuegt.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from app.database import SessionLocal, engine, Base
from app.models.company import Company, ContactPerson, Dossier
from app.models.membership import MembershipFee, PaymentRecord
from app.models.event import Event
from app.models.registration import EventRegistration
from app.models.user import AdminUser
from app.models.ai import AIScore, EmailLog
from passlib.hash import bcrypt

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Clear existing data
for table in reversed(Base.metadata.sorted_tables):
    db.execute(table.delete())
db.commit()

print("Seeding...")

# =====================================================================
# Admin user
# =====================================================================
admin = AdminUser(username="admin", password_hash=bcrypt.hash("admin123"), full_name="AG City Admin", is_active=True)
db.add(admin)

# =====================================================================
# ECHTE City-Talk Veranstaltungen der AG City Berlin
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
print(f"Seeded: {len(events)} City-Talk Events, Admin-User erstellt")
print("Unternehmen per CSV-Import hinzufuegen: /import")
print("Login: admin / admin123")
db.close()
