"""
Configuration utilities for environment variables and settings.

This module provides configuration classes that read from environment variables
to configure email sending behavior. It supports both MailerSend API and SMTP.
"""
from os import getenv
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Main configuration class for email sending.

    Attributes:
        EMAIL_SENDER (str | None): Display name of the email sender.
        EMAIL_SENDER_ADDRESS (str | None): Email address of the sender.
        EMAIL_RECIPIENT_0_NAME (str | None): Default recipient display name.
        EMAIL_RECIPIENT_0_ADDRESS (str | None): Default recipient email address.
        PROD_MODE (bool): If True, emails are sent; otherwise written to debug file.
        MAILER (str): The mailer client to use ('mailersend' or 'smtp').
    """
    EMAIL_SENDER = getenv("EMAIL_SENDER")
    EMAIL_SENDER_ADDRESS = getenv("EMAIL_SENDER_ADDRESS")
    EMAIL_RECIPIENT_0_NAME = getenv("EMAIL_RECIPIENT_0_NAME")
    EMAIL_RECIPIENT_0_ADDRESS = getenv("EMAIL_RECIPIENT_0_ADDRESS")
    PROD_MODE = getenv("PROD_MODE", "false").lower() == "true"
    MAILER = getenv("MAILER_CLIENT", "mailersend")

class SMTPSettings:
    """SMTP configuration for sending emails via an SMTP server.

    Used when Config.MAILER is set to 'smtp'. All values are read from
    environment variables.

    Attributes:
        HOST (str | None): SMTP server hostname (e.g., 'smtp.gmail.com').
        PORT (str | None): SMTP server port (e.g., '465' for SSL).
        USER (str | None): SMTP authentication username.
        PASS (str | None): SMTP authentication password.
    """
    HOST = getenv("SMTP_HOST")
    PORT = getenv("SMTP_PORT")
    USER = getenv("SMTP_USER")
    PASS = getenv("SMTP_PASS")