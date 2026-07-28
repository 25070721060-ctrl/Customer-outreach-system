"""
email_sender.py
---------------
Sends outreach emails over SMTP. Works with Gmail (with an App Password),
Outlook, or any SMTP provider (SendGrid, Mailgun, your company mail server, etc).

IMPORTANT - before sending real bulk email:
- Always include a clear unsubscribe/opt-out option (legally required in most
  places: CAN-SPAM in the US, GDPR/PECR in the EU/UK, etc).
- Don't send from a personal inbox at high volume - it will get flagged as spam
  and can get the account restricted. Use a proper sending domain / ESP for
  anything beyond a handful of test emails.
- Respect rate limits (a small delay between sends) to avoid provider throttling.
"""

import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(
    to_email: str,
    subject: str,
    body: str,
    smtp_host: str,
    smtp_port: int,
    smtp_username: str,
    smtp_password: str,
    sender_name: str = "",
) -> tuple[bool, str]:
    """
    Sends a single email. Returns (success: bool, message: str).
    """
    try:
        msg = MIMEMultipart()
        msg["From"] = f"{sender_name} <{smtp_username}>" if sender_name else smtp_username
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, to_email, msg.as_string())

        return True, "sent"
    except Exception as e:
        return False, str(e)


def send_bulk_emails(
    leads: list[dict],
    subject_template: str,
    body_template: str,
    smtp_config: dict,
    delay_seconds: float = 2.0,
) -> list[dict]:
    """
    Sends personalized emails to a list of leads.

    Each lead dict should have at least an "email" key. subject_template and
    body_template can use Python .format() placeholders matching lead dict
    keys, e.g. "Hi {first_name}, ...".

    Returns a list of dicts with the send result per lead, for logging in
    the dashboard.
    """
    results = []
    for lead in leads:
        try:
            subject = subject_template.format(**lead)
            body = body_template.format(**lead)
        except KeyError as e:
            results.append({"email": lead.get("email"), "success": False, "message": f"missing field {e}"})
            continue

        success, message = send_email(
            to_email=lead["email"],
            subject=subject,
            body=body,
            smtp_host=smtp_config["host"],
            smtp_port=smtp_config["port"],
            smtp_username=smtp_config["username"],
            smtp_password=smtp_config["password"],
            sender_name=smtp_config.get("sender_name", ""),
        )
        results.append({"email": lead["email"], "success": success, "message": message})
        time.sleep(delay_seconds)  # be gentle on the SMTP server / avoid spam flags

    return results
