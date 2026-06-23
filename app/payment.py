"""Build UPI payment links for workshop fees."""

from __future__ import annotations

import os
from urllib.parse import quote


def _price(name: str, default: str) -> float:
    raw = os.getenv(name, default)
    try:
        return max(0.0, float(raw))
    except ValueError:
        return float(default)


def price_per_seat(offer: str) -> float:
    if offer == "Early Bird":
        return _price("WORKSHOP_PRICE_EARLY_BIRD", "599")
    return _price("WORKSHOP_PRICE_STANDARD", "799")


def amount_due(offer: str, seats: int) -> float:
    return round(price_per_seat(offer) * seats, 2)


def upi_configured() -> bool:
    return bool(os.getenv("UPI_VPA", "").strip())


def payment_details(*, offer: str, seats: int, payer_name: str) -> dict | None:
    vpa = os.getenv("UPI_VPA", "").strip()
    if not vpa:
        return None

    payee = os.getenv("UPI_PAYEE_NAME", "Dhruvs Creations").strip()
    per_seat = price_per_seat(offer)
    total = amount_due(offer, seats)
    note = f"Terrarium Workshop - {payer_name}"[:50]

    params = (
        f"pa={quote(vpa)}"
        f"&pn={quote(payee)}"
        f"&am={total:.2f}"
        f"&cu=INR"
        f"&tn={quote(note)}"
    )
    upi_link = f"upi://pay?{params}"

    return {
        "upi_id": vpa,
        "payee_name": payee,
        "price_per_seat": per_seat,
        "amount_due": total,
        "currency": "INR",
        "upi_link": upi_link,
        "note": note,
    }


def public_pricing() -> dict:
    return {
        "early_bird_per_seat": _price("WORKSHOP_PRICE_EARLY_BIRD", "599"),
        "standard_per_seat": _price("WORKSHOP_PRICE_STANDARD", "799"),
        "upi_configured": upi_configured(),
    }
