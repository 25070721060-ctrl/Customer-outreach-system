# Lead Gen & Outreach Dashboard - Setup Guide

## 1. Install the tools (one-time)

1. **Install VS Code**: https://code.visualstudio.com/download
2. **Install Python** (3.10+): https://www.python.org/downloads/
   - On Windows, during install, tick "Add Python to PATH".
   - Check it worked: open a terminal and run `python --version` (Mac/Linux might need `python3 --version`).
3. Open VS Code, go to the Extensions icon (left sidebar, looks like 4 squares), and install:
   - **Python** (by Microsoft)
   - **Pylance** (usually installs automatically with Python)

## 2. Get the project into VS Code

1. Create a folder anywhere on your computer, e.g. `Documents/lead-gen-dashboard`.
2. Put these 5 files into it (all provided alongside this guide):
   - `app.py`
   - `lead_finder.py`
   - `email_sender.py`
   - `requirements.txt`
   - `.env.example`
3. In VS Code: **File → Open Folder** → select that folder.

## 3. Set up a virtual environment (keeps dependencies isolated)

Open the built-in terminal in VS Code: **Terminal → New Terminal** (or `` Ctrl+` ``).

```bash
# Create the virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

You'll know it worked because your terminal prompt will show `(venv)` at the start.

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

## 5. Set up your API keys and email credentials

1. Copy `.env.example` to a new file named `.env` in the same folder.
2. Fill in the values:
   - **Google Custom Search**: get a key at https://console.cloud.google.com/apis/credentials and set up a search engine at https://programmablesearchengine.google.com/
   - **Hunter.io**: sign up free at https://hunter.io/ and get your API key from https://hunter.io/api-keys
   - **SMTP (sending email)**: if using Gmail, turn on 2-Step Verification, then create an "App Password" at https://myaccount.google.com/apppasswords - use that as `SMTP_PASSWORD`, not your normal Gmail password.
3. `.env` is where your real secrets live - never share this file or upload it anywhere public. (If this project ever goes on GitHub, add `.env` to a `.gitignore` file.)

## 6. Run the dashboard

```bash
streamlit run app.py
```

This opens the dashboard in your browser automatically (usually at `http://localhost:8501`). Leave the terminal running - closing it stops the dashboard.

## 7. Using it

- **Find Leads tab**: search Google for companies, or search Hunter.io by domain to pull real emails.
- **Lead Data tab**: view everything collected so far, export to CSV, or import a CSV of leads you already have.
- **Send Emails tab**: write your subject/body (use `{first_name}` etc. as placeholders), pick which leads to email, and send. **Fill in real product details in the body template before sending anything real.**

## What you'll likely need to customize once you get the product details

- The email `body_template` in the Send Emails tab (or hard-code a better default inside `app.py`).
- The Google search queries you use to find relevant companies (industry-specific keywords).
- Possibly swap Hunter.io for another provider (Apollo.io, Snov.io) if your company already has an account there - the function shape in `lead_finder.py` stays the same, just the API call changes.

## Notes on doing this responsibly

- Don't scrape LinkedIn directly - it violates their Terms of Service and can get an account banned. Use LinkedIn Sales Navigator or a licensed data provider instead.
- Always give recipients an easy way to opt out (there's a line for this in the default template) - this isn't just courtesy, it's legally required in most countries for commercial email (CAN-SPAM, GDPR/PECR, etc.).
- Keep send volume low and add delays (already built into `email_sender.py`) - sending too fast from a personal account gets flagged as spam.
