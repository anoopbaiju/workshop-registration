"""Append workshop registrations to a Google Sheet."""

from __future__ import annotations

import json
import os
from datetime import datetime
from functools import lru_cache
from zoneinfo import ZoneInfo

import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
EARLY_BIRD_LIMIT = 10

HEADERS = [
    "Timestamp (IST)",
    "Full Name",
    "WhatsApp Number",
    "Email",
    "Age Group",
    "Number of Seats",
    "How did you hear about us?",
    "Message",
    "Offer",
    "Status",
]


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


def registration_count() -> int:
    ws = _sheet()
    values = ws.get_all_values()
    if len(values) <= 1:
        return 0
    return len(values) - 1


def early_bird_remaining() -> int:
    return max(0, EARLY_BIRD_LIMIT - registration_count())


def ensure_headers() -> None:
    ws = _sheet()
    first_row = ws.row_values(1)
    if first_row != HEADERS:
        ws.update("A1:J1", [HEADERS])
        ws.format(
            "A1:J1",
            {
                "textFormat": {"bold": True},
                "backgroundColor": {"red": 0.18, "green": 0.29, "blue": 0.18},
                "horizontalAlignment": "CENTER",
            },
        )


def append_registration(data: dict) -> dict:
    ensure_headers()
    remaining_before = early_bird_remaining()
    offer = "Early Bird" if remaining_before > 0 else "Standard"

    now = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")
    row = [
        now,
        data["full_name"],
        data["whatsapp"],
        data["email"],
        data["age_group"],
        str(data["seats"]),
        data.get("source") or "",
        data.get("message") or "",
        offer,
        "New",
    ]
    _sheet().append_row(row, value_input_option="USER_ENTERED")

    return {
        "offer": offer,
        "seats": data["seats"],
        "early_bird_remaining": max(0, remaining_before - 1),
    }
