#!/usr/bin/env python3
"""Test Google Sheets connection and create column headers."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

sys.path.insert(0, str(ROOT))

from app.sheets import HEADERS, ensure_headers, _sheet  # noqa: E402


def main() -> int:
    sheet_id = os.getenv("GOOGLE_SHEET_ID", "")
    creds_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "")

    if not sheet_id or sheet_id == "your_google_sheet_id_from_url":
        print("Set GOOGLE_SHEET_ID in .env first.")
        return 1

    creds_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "")
    creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()

    if not creds_json and (not creds_path or creds_path == "credentials/service-account.json"):
        creds_file = ROOT / "credentials" / "service-account.json"
    elif creds_path:
        creds_file = ROOT / creds_path
    else:
        creds_file = None

    if not creds_json and (not creds_file or not creds_file.is_file()):
        print(f"Service account file not found: {creds_path}")
        print("Save your Google JSON key to credentials/service-account.json")
        return 1

    try:
        ws = _sheet()
        title = ws.spreadsheet.title
        ensure_headers()
    except Exception as exc:
        print(f"Connection failed: {exc}")
        print("\nChecklist:")
        print("1. Google Sheets API is enabled in Google Cloud")
        print("2. Sheet is shared with the service account email (Editor)")
        print("3. GOOGLE_SHEET_ID is correct")
        return 1

    print(f"Connected to spreadsheet: {title}")
    print(f"Headers ready ({len(HEADERS)} columns):")
    for col in HEADERS:
        print(f"  - {col}")
    print("\nGoogle Sheet is ready for registrations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
