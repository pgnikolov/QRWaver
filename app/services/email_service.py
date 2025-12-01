"""Simple email sending service using SMTP.

Reads SMTP configuration from settings and sends emails. Supports plain-text
and optional HTML content. In development, if SMTP is not configured, it
falls back to printing the email contents to the console/logs.
"""

import smtplib
from email.message import EmailMessage
from typing import Optional
from urllib.parse import urlparse

from flask import render_template
from app.config.settings import (
    MAIL_SERVER,
    MAIL_PORT,
    MAIL_USERNAME,
    MAIL_PASSWORD,
    MAIL_USE_TLS,
    MAIL_USE_SSL,
    MAIL_DEFAULT_SENDER,
    PUBLIC_BASE_URL,
)


class EmailService:
    @staticmethod
    def send_email(
        to: str,
        subject: str,
        body: str,
        sender: Optional[str] = None,
        html_body: Optional[str] = None,
    ) -> bool:
        sender = sender or MAIL_DEFAULT_SENDER

        # Fallback: no SMTP configured → print and pretend success
        if not MAIL_SERVER:
            print("[EmailService] SMTP not configured. Email contents below:")
            print(f"To: {to}\nFrom: {sender}\nSubject: {subject}\n\n{body}")
            if html_body:
                print("\n[EmailService] HTML preview:\n" + html_body)
            return True

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = to
        # Always include a plain-text part
        msg.set_content(body)
        # Optional HTML alternative for better rendering
        if html_body:
            msg.add_alternative(html_body, subtype="html")

        try:
            if MAIL_USE_SSL:
                with smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT, timeout=10) as server:
                    if MAIL_USERNAME and MAIL_PASSWORD:
                        server.login(MAIL_USERNAME, MAIL_PASSWORD)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(MAIL_SERVER, MAIL_PORT, timeout=10) as server:
                    if MAIL_USE_TLS:
                        server.starttls()
                    if MAIL_USERNAME and MAIL_PASSWORD:
                        server.login(MAIL_USERNAME, MAIL_PASSWORD)
                    server.send_message(msg)
            return True
        except Exception as e:
            print("[EmailService] Failed to send email:", e)
            return False

    @staticmethod
    def send_confirmation_email(to: str, confirm_url: str) -> bool:
        subject = "Confirm your QRWaver account"
        body = (
            "Welcome to QRWaver!\n\n"
            "Please confirm your email address by clicking the link below:\n"
            f"{confirm_url}\n\n"
            "This link will expire in 24 hours. If you did not sign up, you can ignore this email."
        )

        # Derive a base URL for assets: prefer PUBLIC_BASE_URL, else from confirm_url
        base_url = PUBLIC_BASE_URL or ""
        if not base_url:
            try:
                parsed = urlparse(confirm_url)
                base_url = f"{parsed.scheme}://{parsed.netloc}"
            except Exception:
                base_url = ""

        # Render an HTML version using a Jinja2 template
        try:
            html_body = render_template(
                "emails/confirm_email.html",
                confirm_url=confirm_url,
                base_url=base_url.rstrip("/"),
            )
        except Exception:
            # If template rendering fails for any reason, fall back to text-only
            html_body = None

        return EmailService.send_email(
            to=to,
            subject=subject,
            body=body,
            html_body=html_body,
        )
