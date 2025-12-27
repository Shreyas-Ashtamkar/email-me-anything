
"""
Entry point for the generalized email-me-anything project. (only if you clone this repo and run this file directly)
"""
from src.email_me_anything import send_lucky_email

if __name__ == "__main__":
    send_lucky_email(
        subject="Your Daily Inspiration!",
        csv_path="quotes.example.csv",
        template_path="example.html",
        recipients=[{"email": "shreyas.ashtamkar18@gmail.com", "name": "Shreyas"}],
        variable_map={
            "id": "ID",
            "quote": "Quote",
            "author": "Author"
        }
    )
