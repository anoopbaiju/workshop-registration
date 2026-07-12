"""Append workshop registrations to a Google Sheet."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from urllib.parse import quote
from functools import lru_cache
from zoneinfo import ZoneInfo

import gspread
from google.oauth2.service_account import Credentials

from app.payment import amount_due
from app.workshop import confirmation_message

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

HEADERS = [
    "Timestamp (IST)",
    "Registration ID",
    "Full Name",
    "WhatsApp Number",
    "Email",
    "Age Group",
    "Number of Seats",
    "How did you hear about us?",
    "Message",
    "Amount Due (INR)",
    "UPI Ref / UTR",
    "Status",
    "WhatsApp Confirm Link",
]


def whatsapp_confirm_link(name: str, whatsapp: str) -> str:
    """Pre-filled wa.me link for organizer to send after payment is verified."""
    digits = whatsapp.lstrip("+").replace(" ", "")
    return f"https://wa.me/{digits}?text={quote(confirmation_message(name))}"


def _credentials() -> Credentials:
    raw_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    if raw_json:
        info = json.loads(raw_json)
        return Credentials.from_service_account_info(info, scopes=SCOPES)

    path = os.environ["GOOGLE_SERVICE_ACCOUNT_FILE"]
    return Credentials.from_service_account_file(path, scopes=SCOPES)


@lru_cache(maxsize=1)
def _client() -> gspread.Client:
    return gspread.authorize(_credentials())


def _sheet():
    sheet_id = os.environ["GOOGLE_SHEET_ID"]
    return _client().open_by_key(sheet_id).sheet1


def ensure_headers() -> None:
    ws = _sheet()
    first_row = ws.row_values(1)
    if first_row != HEADERS:
        ws.update("A1:M1", [HEADERS])
        ws.format(
            "A1:M1",
            {
                "textFormat": {"bold": True},
                "backgroundColor": {"red": 0.18, "green": 0.29, "blue": 0.18},
                "horizontalAlignment": "CENTER",
            },
        )


def _find_row_for_registration(registration_id: str) -> int | None:
    ws = _sheet()
    values = ws.get_all_values()
    for idx, row in enumerate(values[1:], start=2):
        if len(row) > 1 and row[1] == registration_id:
            return idx
    return None


def _parse_row(row: list[str]) -> dict | None:
    if len(row) < 2 or not row[1].strip():
        return None

    padded = row + [""] * max(0, len(HEADERS) - len(row))
    name = padded[2]
    whatsapp = padded[3]
    return {
        "timestamp": padded[0],
        "registration_id": padded[1],
        "full_name": name,
        "whatsapp": whatsapp,
        "email": padded[4],
        "age_group": padded[5],
        "seats": padded[6],
        "source": padded[7],
        "message": padded[8],
        "amount_due": padded[9],
        "upi_reference": padded[10],
        "status": padded[11] or "Pending payment",
        "whatsapp_confirm_link": padded[12] or whatsapp_confirm_link(name, whatsapp),
    }


def list_registrations(status: str | None = None) -> list[dict]:
    ensure_headers()
    results: list[dict] = []
    for row in _sheet().get_all_values()[1:]:
        parsed = _parse_row(row)
        if parsed is None:
            continue
        if status and parsed["status"] != status:
            continue
        results.append(parsed)
    return results


def create_pending_registration(data: dict) -> dict:
    ensure_headers()
    registration_id = uuid.uuid4().hex[:8].upper()
    total = amount_due(data["seats"])
    now = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")

    row = [
        now,
        registration_id,
        data["full_name"],
        data["whatsapp"],
        data["email"],
        data["age_group"],
        str(data["seats"]),
        data.get("source") or "",
        data.get("message") or "",
        f"{total:.2f}",
        "",
        "Pending payment",
        whatsapp_confirm_link(data["full_name"], data["whatsapp"]),
    ]
    _sheet().append_row(row, value_input_option="USER_ENTERED")

    return {
        "registration_id": registration_id,
        "seats": data["seats"],
        "amount_due": total,
    }


def claim_payment(registration_id: str, upi_reference: str) -> None:
    ensure_headers()
    row_idx = _find_row_for_registration(registration_id)
    if row_idx is None:
        raise ValueError("Registration not found")

    ws = _sheet()
    status = ws.cell(row_idx, 12).value
    if status in {"Awaiting verification", "Confirmed"}:
        return

    if status != "Pending payment":
        raise ValueError("Payment cannot be submitted for this registration")

    ws.update_cell(row_idx, 11, upi_reference)
    ws.update_cell(row_idx, 12, "Awaiting verification")


def confirm_registration(registration_id: str) -> dict:
    ensure_headers()
    row_idx = _find_row_for_registration(registration_id.upper())
    if row_idx is None:
        raise ValueError("Registration not found")

    ws = _sheet()
    status = ws.cell(row_idx, 12).value or ""
    name = ws.cell(row_idx, 3).value or ""
    whatsapp = ws.cell(row_idx, 4).value or ""
    link = whatsapp_confirm_link(name, whatsapp)
    ws.update_cell(row_idx, 13, link)

    if status == "Confirmed":
        return {
            "registration_id": registration_id.upper(),
            "full_name": name,
            "status": "Confirmed",
            "already_confirmed": True,
            "whatsapp_confirm_link": link,
        }

    if status != "Awaiting verification":
        raise ValueError(f"Cannot confirm — status is '{status}'")

    ws.update_cell(row_idx, 12, "Confirmed")
    return {
        "registration_id": registration_id.upper(),
        "full_name": name,
        "status": "Confirmed",
        "already_confirmed": False,
        "whatsapp_confirm_link": link,
    }
