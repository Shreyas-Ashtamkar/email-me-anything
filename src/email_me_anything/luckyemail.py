
"""
Generalized orchestration logic for sending any row of data via email using a template.
"""
from pathlib import Path

from .config import (
        PROD_MODE, 
        EMAIL_RECIPIENT_0_ADDRESS, 
        EMAIL_RECIPIENT_0_NAME, 
        EMAIL_SENDER, 
        EMAIL_SENDER_ADDRESS
    )

from .csvutils import select_random_row
from .emailutils import build_html_content, send_email

def send_lucky_email(
    csv_path: Path,
    template_path: Path,
    sender_address: str = EMAIL_SENDER_ADDRESS,
    sender_name: str = EMAIL_SENDER,
    recipients: list = [{"email": EMAIL_RECIPIENT_0_ADDRESS, "name": EMAIL_RECIPIENT_0_NAME}],
    variable_map: dict=None,
    subject: str = None,
    output_html_path: Path = Path("debug-email.html")
) -> bool:
    
    selected_data = select_random_row(csv_path)
    if not selected_data:
        print("No row selected.")
        return False
        
    html_content = build_html_content(template_path, selected_data, variable_map)

    if not subject:
        subject = "New Data Row!"
        
    sender = {"email": sender_address, "name": sender_name}
    recipients = recipients
    
    if PROD_MODE:
        response = send_email(
            sender,
            recipients,
            subject,
            html_content
        )
        print(f"Email sent: {response}")
    else:
        print("Production mode is OFF. Writing email to debug-email.html")
        with open(output_html_path, "w", encoding="utf-8") as debug_file:
            debug_file.write(html_content)
    return True
