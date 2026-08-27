"""SevaSetu AI — Email Service | Rahul Jha | Made in India 🇮🇳"""
import logging
from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings

logger = logging.getLogger(__name__)

async def _send_email(to_email: str, subject: str, body: str) -> None:
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP is not configured; email was not sent to %s", to_email)
        return
    message = EmailMessage()
    message["From"] = f"{settings.FROM_NAME} <{settings.FROM_EMAIL or settings.SMTP_USER}>"
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)
    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        start_tls=True,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        timeout=20,
    )

async def send_welcome_email(email: str, name: str, language: str = "en"):
    messages = {
        "en": f"Welcome to SevaSetu AI, {name}! 🇮🇳",
        "hi": f"SevaSetu AI में आपका स्वागत है, {name}! 🇮🇳",
        "mr": f"SevaSetu AI मध्ये आपले स्वागत आहे, {name}! 🇮🇳",
    }
    try:
        await _send_email(email, "Welcome to SevaSetu AI 🇮🇳", messages.get(language, messages["en"]))
    except Exception:
        logger.exception("Failed to send welcome email to %s", email)

async def send_password_reset_email(email: str, name: str, reset_url: str):
    body = (
        f"Hello {name},\n\n"
        "We received a request to reset your SevaSetu AI password.\n\n"
        f"Use this link within 30 minutes:\n{reset_url}\n\n"
        "If you did not request this, you can safely ignore this email.\n\n"
        "SevaSetu AI 🇮🇳"
    )
    try:
        await _send_email(email, "Reset your SevaSetu AI password", body)
    except Exception:
        logger.exception("Failed to send password reset email to %s", email)

async def send_report_email(email: str, name: str, report_path: str):
    logger.info("📧 Report email → %s: %s", email, report_path)
