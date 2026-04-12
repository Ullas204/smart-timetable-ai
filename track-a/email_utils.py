import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("EMAIL_PASSWORD")


def send_email(subject, message, to_email):
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print("Email Error:", e)
        return False