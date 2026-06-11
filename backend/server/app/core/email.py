from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_PLACEHOLDER_KEYS = {"", "RESEND_KEY", "your-resend-key"}


def send_otp_email(email: str, code: str) -> None:
    """
    Send the OTP verification code via Resend.

    When no real RESEND_KEY is configured (dev), the code is logged instead of
    sent so the flow remains usable locally.
    """
    settings = get_settings()
    key = settings.RESEND_KEY

    if key in _PLACEHOLDER_KEYS:
        logger.warning(
            "RESEND_KEY not configured - OTP for %s is %s (not emailed)", email, code
        )
        return

    try:
        import resend

        resend.api_key = key
        resend.Emails.send(
            {
                "from": settings.RESEND_FROM,
                "to": [email],
                "subject": "Your WebDissect verification code",
                "html": (
                    "<p>Your WebDissect verification code is:</p>"
                    f"<h2 style='letter-spacing:4px'>{code}</h2>"
                    f"<p>It expires in {settings.OTP_EXPIRE_MINUTES} minutes.</p>"
                ),
            }
        )
        logger.info("OTP email sent to %s", email)
    except Exception:  # pragma: no cover - external service failure
        logger.exception("Failed to send OTP email to %s; code=%s", email, code)
