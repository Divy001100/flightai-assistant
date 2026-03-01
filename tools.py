import sqlite3
import os
from datetime import datetime

DB_PATH = "data/prices.db"

def init_database():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            city TEXT PRIMARY KEY,
            price INTEGER NOT NULL
        )
    """)
    
    sample = [
        ("paris", 620), ("london", 480), ("new york", 890), ("tokyo", 1150),
        ("dubai", 720), ("bangkok", 650), ("rome", 550), ("sydney", 1350),
        ("barcelona", 580), ("amsterdam", 520), ("singapore", 980), ("hong kong", 920),
        ("istanbul", 480), ("miami", 750), ("los angeles", 820), ("cape town", 1100),
        ("bali", 680), ("santorini", 670), ("marrakech", 590), ("rio de janeiro", 980)
    ]
    cur.executemany("INSERT OR IGNORE INTO prices (city, price) VALUES (?, ?)", sample)
    conn.commit()
    conn.close()
    print("Database ready.")

def get_ticket_price(city: str) -> str:
    init_database()
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT price FROM prices WHERE city = LOWER(?)", (city.strip(),))
        row = cur.fetchone()
        if row:
            return f"💶 Return economy ticket to **{city.title()}** ≈ **€{row[0]}** (taxes included)."
        return f"ℹ️ No current price available for **{city.title()}**."

def start_booking_process(
    destination: str,
    date: str,
    passengers: int,
    lead_passenger_name: str,
    email: str,
    travel_class: str = "Economy"
) -> str:
    """Called ONLY when ALL booking information is collected."""
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return "Invalid date format. Please use YYYY-MM-DD."

    ref = f"FA{abs(hash(destination + date + lead_passenger_name)) % 1000000:06d}"

    return f"""
🎉 **Booking Confirmed!**

**Lead passenger:** {lead_passenger_name}
**Destination:** {destination.title()}
**Date:** {date}
**Passengers:** {passengers}
**Travel class:** {travel_class}
**Booking reference:** **{ref}**

A confirmation email has been sent to **{email}**.  
Thank you for choosing FlightAI — have a wonderful trip! ✈️
"""