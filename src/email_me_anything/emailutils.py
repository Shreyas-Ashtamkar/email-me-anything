"""Email utilities for building and sending emails.

Supports both MailerSend API and SMTP for sending emails based on configuration.

Functions:
- build_context: Creates a context dictionary for template rendering.
- build_html_content: Renders an HTML template with provided data.
- send_email: Sends an email via the configured mailer (MailerSend or SMTP).
"""
from pathlib import Path
from typing import Any, Dict, List

from mailersend import MailerSendClient, EmailBuilder

from email.message import EmailMessage
from email.utils import formataddr
from email_me_anything.config import Config, SMTPSettings
import smtplib, ssl

def build_context(data: Dict[str, Any], variable_map: Dict[str, str] = None) -> Dict[str, Any]:
    """
    Build a context dictionary by mapping data keys to template variables.
    Args:
        data: A dictionary containing the source data to be mapped.
        variable_map: Optional dictionary mapping template variable names to data keys.
                     If None, returns the data dictionary as-is.
    Returns:
        A dictionary containing the context for template rendering. If variable_map is None,
        returns the original data dictionary. Otherwise, returns a new dictionary with template
        variable names as keys and corresponding values from data (or empty strings if keys
        are not found).
    Example:
        >>> data = {"user_name": "John", "email": "john@example.com"}
        >>> var_map = {"name": "user_name", "contact": "email"}
        >>> build_context(data, var_map)
        {"name": "John", "contact": "john@example.com"}
    """
    
    context = {}
    if variable_map is None:
        context = data
    else:
        for template_var, data_key in variable_map.items():
            context[template_var] = data.get(data_key, "")
    return context
        
def build_html_content(template_path: Path, data: Dict[str, Any], variable_map: Dict[str, Any] = None) -> str:
    """
    Build HTML content by rendering a template with provided data.

    Args:
        template_path (Path): Path to the HTML template file.
        data (Dict[str, Any]): Dictionary containing data to be used in the template.
        variable_map (Dict[str, Any], optional): Optional mapping to transform or alias variables
            from the data dictionary. Defaults to None.

    Returns:
        str: Rendered HTML content with variables substituted from the context.

    Raises:
        FileNotFoundError: If the template file does not exist at template_path.
        KeyError: If a required variable in the template is missing from the context.
        UnicodeDecodeError: If the template file cannot be decoded as UTF-8.
    """
    
    context = build_context(data, variable_map)
    with open(template_path, "r", encoding="utf-8") as file:
        html_template = file.read()
    return html_template.format_map(context)

def send_email(sender: Dict[str, str], recipients: List[Dict[str, str]], subject: str, html_content: str) -> Dict[str, Any]:
    """Send an email using the configured mailer service (MailerSend or SMTP).

    The mailer is selected based on Config.MAILER ('mailersend' or 'smtp').
    When PROD_MODE is False, no email is sent and the HTML content is written
    to 'debug-email.html' for inspection.

    Args:
        sender (Dict[str, str]): A dictionary containing the sender's email address and name.
            Expected keys: "email" (str), "name" (str).
        recipients (List[Dict[str, str]]): A list of dictionaries containing recipient information.
            Each dictionary should contain "email" and "name" keys.
        subject (str): The subject line of the email.
        html_content (str): The HTML-formatted body content of the email.

    Returns:
        Dict[str, Any]: A dictionary containing the response from the mailer service.
            In debug mode, returns {"status": "debug", "message": "..."}.

    Raises:
        Exception: May raise exceptions from the mailer client if the email
            fails to send (e.g., invalid email addresses, authentication errors).

    Example:
        >>> sender = {"email": "from@example.com", "name": "John Doe"}
        >>> recipients = [{"email": "to@example.com", "name": "Jane Smith"}]
        >>> response = send_email(sender, recipients, "Hello", "<p>Hello World</p>")
    """
    
    if Config.PROD_MODE:
        if Config.MAILER=="mailersend":
            ms = MailerSendClient()
            email = (
                EmailBuilder()
                .from_email(sender["email"], sender["name"])
                .to_many(recipients)
                .subject(subject)
                .html(html_content)
                .build()
            )
            response = ms.emails.send(email).to_dict()
        elif Config.MAILER=="smtp":
            print(SMTPSettings)
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = formataddr((sender["name"], sender["email"]))
            msg["To"] = recipients[0]["email"]
            msg.set_content("Your email does not support HTML content")
            msg.add_alternative(html_content, subtype="html")
            
            ctx = ssl.create_default_context()
            response = None
            with smtplib.SMTP_SSL(SMTPSettings.HOST, SMTPSettings.PORT, context=ctx,timeout=30) as server:
                server.ehlo() # If failed here HOST or PORT Wrong                 
                server.login(SMTPSettings.USER, SMTPSettings.PASS) # If failed here USER or PASS wrong
                response = server.send_message(msg) # If failed here issue sending mail (check sender/reciever email address or content or attachment)
            if response:
                response = dict(response)
            else:
                response = {"status": "success", "message":"email sent successfully"}
                
        else:
            print("Some error happened need to debug. See emailutils.py:94")
    else:
        response = {"status": "debug", "message": "Email not sent in non-production mode."}
        print("Production mode is OFF. Writing email to debug-email.html")
        with open("debug-email.html", "w", encoding="utf-8") as debug_file:
            debug_file.write(html_content)
    return response
