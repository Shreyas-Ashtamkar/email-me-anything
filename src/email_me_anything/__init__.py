# Expose main modules for easy import
from .config import EMAIL_SENDER, EMAIL_SENDER_ADDRESS, EMAIL_RECIPIENT_0_NAME, EMAIL_RECIPIENT_0_ADDRESS, PROD_MODE
from .csvutils import read_csv, select_random_row
from .emailutils import build_html_content, send_email, build_context
from .luckyemail import send_lucky_email
