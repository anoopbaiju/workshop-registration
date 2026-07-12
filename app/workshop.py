"""Shared workshop details shown on the site and in confirmation messages."""

WORKSHOP_TITLE = "Moss & Magic"
WORKSHOP_DATE = "Thursday, 23 July 2026"
WORKSHOP_TIME = "10:30 AM to 12:30 PM"
WORKSHOP_VENUE_NAME = "Sharanya"
WORKSHOP_VENUE_LINES = [
    "House no: 36",
    "Near SFS Richmond Apartment",
    "Sashtamangalam",
]
WORKSHOP_MAPS_URL = "https://maps.google.com/?q=8.515356,76.973564"


def venue_one_line() -> str:
    return f"{WORKSHOP_VENUE_NAME}, {', '.join(WORKSHOP_VENUE_LINES)}"


def confirmation_message(name: str) -> str:
    """WhatsApp confirmation text sent after payment is verified."""
    address = "\n".join(WORKSHOP_VENUE_LINES)
    return (
        f"Hi {name}, ✅ Your slot for *Moss & Magic* terrarium workshop by Dhruvscreations is confirmed!\n\n"
        f"📅 *Date:* {WORKSHOP_DATE}\n"
        f"🕙 *Time:* {WORKSHOP_TIME}\n"
        f"📍 *Venue:* {WORKSHOP_VENUE_NAME}\n"
        f"{address}\n"
        f"🗺️ {WORKSHOP_MAPS_URL}\n\n"
        f"We look forward to seeing you! – Devu"
    )
