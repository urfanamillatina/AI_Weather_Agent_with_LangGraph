"""
notify_tool.py
---------------
Utility functions for sending notifications via Email (SMTP) and WhatsApp/SMS (Twilio).

Functions
---------
send_email(body: str, subject: str = "🌦️ Your AI Weather Agent Update") -> bool
    Sends the email with the given body/subject using Gmail SMTP over SSL.
    Returns True on success, False on failure or if not configured.

send_whatsapp(body: str) -> bool
    Sends a WhatsApp/SMS message via Twilio API using environment variables.
    Returns True on success, False on failure or if not configured.

Tips
----
• Gmail usually requires an "App Password" when 2FA is enabled.
• Twilio WhatsApp Sandbox requires joining the sandbox and using the sandbox number.
"""
import os
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client

def send_email(body: str, subject: str = "🌦️ Your AI Weather Agent Update") -> bool:
    """Send an email using SMTP/SSL; return True if sent, else False."""
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    recipient = os.getenv("EMAIL_TO") or sender
    if not (sender and password and recipient):
        print("Email not configured. Skipping email.")
        return False
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(sender, password)
            s.send_message(msg)
        print(f"📧 Email sent to {recipient}")
        return True
    except Exception as e:
        print("Email error:", e)
        return False

def send_whatsapp(body: str) -> bool:
    """Send a WhatsApp/SMS via Twilio; return True if sent, else False."""
    sid = os.getenv("TWILIO_SID")
    auth = os.getenv("TWILIO_AUTH")
    from_no = os.getenv("TWILIO_FROM")
    to_no = os.getenv("TWILIO_TO")
    if not all([sid, auth, from_no, to_no]):
        print("Twilio not configured. Skipping WhatsApp/SMS.")
        return False
    try:
        client = Client(sid, auth)
        client.messages.create(from_=from_no, to=to_no, body=body)
        print(f"📱 WhatsApp/SMS sent to {to_no}")
        return True
    except Exception as e:
        print("Twilio error:", e)
        return False
