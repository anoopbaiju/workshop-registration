"""Build UPI payment details for workshop fees."""

from __future__ import annotations

import os
from urllib.parse import quote


def price_per_seat() -> float:
    raw = os.getenv("WORKSHOP_PRICE_PER_SEAT", "3000")
    try:
        return max(0.0, float(raw))
    except ValueError:
        return 3000.0


def amount_due(seats: int) -> float:
    return round(price_per_seat() * seats, 2)


def payment_details(*, seats: int, payer_name: str, registration_id: str) -> dict:
    vpa = os.getenv("UPI_VPA", "alwaysdevu@ybl").strip()
    payee = os.getenv("UPI_PAYEE_NAME", "DEVU M").strip()
    per_seat = price_per_seat()
    total = amount_due(seats)
    note = f"Moss Magic {registration_id} - {payer_name}"[:50]

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
        "seats": seats,
        "amount_due": total,
        "currency": "INR",
        "upi_link": upi_link,
        "qr_image_url": f"https://api.qrserver.com/v1/create-qr-code/?size=260x260&data={quote(upi_link)}",
        "static_qr_path": "/static/images/upi-qr.png",
        "note": note,
    }


def public_pricing() -> dict:
    per_seat = price_per_seat()
    return {
        "price_per_seat": per_seat,
        "currency": "INR",
    }
