# Terrarium Workshop Registration

Mobile-friendly registration page for **Dhruvs Creations — Terrarium Workshop**.  
**Thursday, 23 July 2026** · Sharanya, Shastamangalam, Trivandrum.

Share the link on WhatsApp; each submission is saved automatically to your **Google Sheet**.

---

## Quick start (Google Sheet + form)

### Step 1 — Create the Google Sheet

1. Go to [sheets.google.com](https://sheets.google.com) → **Blank spreadsheet**
2. Name it `Terrarium Workshop Registrations`
3. Copy the **Sheet ID** from the URL:
   ```
   https://docs.google.com/spreadsheets/d/PASTE_THIS_PART/edit
   ```

### Step 2 — Google Cloud service account

1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (e.g. `dhruvs-workshop`)
3. **APIs & Services → Library** → enable **Google Sheets API**
4. **Credentials → Create credentials → Service account**
5. Open the service account → **Keys → Add key → JSON**
6. Save the file as:
   ```
   workshop-registration/credentials/service-account.json
   ```

### Step 3 — Share the sheet

1. Open the JSON file and copy `client_email` (ends with `@....iam.gserviceaccount.com`)
2. In Google Sheets → **Share** → paste that email → **Editor** → Send

### Step 4 — Configure `.env`

```bash
cd /Users/anoopbaiju/Projects/etoro-news-bot/workshop-registration
cp .env.example .env
```

Edit `.env` and set:

```env
GOOGLE_SHEET_ID=your_actual_sheet_id
GOOGLE_SERVICE_ACCOUNT_FILE=credentials/service-account.json
```

### Step 5 — Test the connection

```bash
source .venv/bin/activate
python setup_google_sheet.py
```

You should see: `Google Sheet is ready for registrations.`

### Step 6 — Run the form

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

Open **http://localhost:8080** — submit a test registration and check your Google Sheet.

---

## Share on WhatsApp

Once deployed with a public URL, send:

> 🌿 Terrarium Workshop — Thursday, 23 July  
> Register here (limited seats): https://your-link.com  
> WhatsApp: +91 95676 02762

---

## Sheet columns

| Column | Source |
|--------|--------|
| Timestamp (IST) | Auto |
| Full Name | Form |
| WhatsApp Number | Form |
| Email | Form |
| Age Group | Form |
| Number of Seats | Form |
| How did you hear about us? | Form |
| Message | Form |
| Offer | `Early Bird` (first 10) or `Standard` |
| Status | `New` — change to `Confirmed` when ready |

---

## Contact

- **Dhruvs Creations**
- **WhatsApp:** [+91 95676 02762](https://wa.me/919567602762)

UPI payment / QR code can be added in a later step.
