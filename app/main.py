"""Moss & Magic registration — form, UPI payment, Google Sheets."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.payment import payment_details, public_pricing
from app.sheets import confirm_registration, create_pending_registration

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"

WHATSAPP_NUMBER = os.getenv("ORG_WHATSAPP_DISPLAY", "+91 95676 02762")
WHATSAPP_LINK = os.getenv("ORG_WHATSAPP_LINK", "https://wa.me/919567602762")

app = FastAPI(title="Moss & Magic — Dhruvs Creations")

origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC), name="static")

AGE_GROUPS = {
    "Child (under 12)",
    "Teen (12–17)",
    "Adult (18+)",
    "Family / mixed ages",
}


class Registration(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    whatsapp: str = Field(min_length=10, max_length=20)
    email: EmailStr
    age_group: str
    seats: int = Field(ge=1, le=10)
    source: str | None = Field(default=None, max_length=120)
    message: str | None = Field(default=None, max_length=500)

    @field_validator("whatsapp")
    @classmethod
    def normalize_whatsapp(cls, value: str) -> str:
        digits = "".join(ch for ch in value if ch.isdigit())
        if len(digits) < 10:
            raise ValueError("Enter a valid WhatsApp number with at least 10 digits")
        if len(digits) == 10:
            digits = "91" + digits
        return "+" + digits

    @field_validator("age_group")
    @classmethod
    def valid_age_group(cls, value: str) -> str:
        if value not in AGE_GROUPS:
            raise ValueError("Please select an age group")
        return value


class PaymentConfirm(BaseModel):
    registration_id: str = Field(min_length=6, max_length=12)


def _sheets_configured() -> bool:
    if os.getenv("GOOGLE_SHEET_ID") and os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"):
        return True
    return bool(os.getenv("GOOGLE_SHEET_ID") and os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE"))


@app.get("/")
@app.head("/")
def index():
    page = STATIC / "index.html"
    if not page.is_file():
        raise HTTPException(500, f"Registration page missing at {page}")
    return FileResponse(page)


@app.get("/health")
@app.head("/health")
def health():
    return {"ok": True}


@app.get("/api/status")
def status():
    return {
        "configured": _sheets_configured(),
        "whatsapp_number": WHATSAPP_NUMBER,
        "whatsapp_link": WHATSAPP_LINK,
        **public_pricing(),
    }


@app.post("/api/register")
def register(payload: Registration):
    if not _sheets_configured():
        raise HTTPException(503, "Registration is not configured yet. Contact the organizer.")

    try:
        result = create_pending_registration(payload.model_dump())
        payment = payment_details(
            seats=result["seats"],
            payer_name=payload.full_name,
            registration_id=result["registration_id"],
        )
    except FileNotFoundError:
        raise HTTPException(503, "Google credentials file not found. Contact the organizer.")
    except Exception as exc:
        raise HTTPException(500, f"Could not save registration: {exc}") from exc

    return {
        "ok": True,
        "registration_id": result["registration_id"],
        "seats": result["seats"],
        "payment": payment,
    }


@app.post("/api/confirm-payment")
def confirm_payment(payload: PaymentConfirm):
    if not _sheets_configured():
        raise HTTPException(503, "Registration is not configured yet. Contact the organizer.")

    try:
        confirm_registration(payload.registration_id.upper())
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(500, f"Could not confirm payment: {exc}") from exc

    return {
        "ok": True,
        "message": (
            "Payment received! Your registration for Moss & Magic is complete. "
            "We'll contact you on WhatsApp with workshop details."
        ),
        "whatsapp_number": WHATSAPP_NUMBER,
        "whatsapp_link": WHATSAPP_LINK,
    }
