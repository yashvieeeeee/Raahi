"""Notification service for Raahi application."""

import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()


class NotificationService:
    def __init__(self):
        self.admin_email = os.getenv("ADMIN_EMAIL", "admin@raahi.local")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")

    def validate_email_or_phone(self, contact):
        email_pattern = r"^[a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        phone_pattern = r"^\d{10}$"

        if re.match(email_pattern, contact):
            return "email"
        if re.match(phone_pattern, contact):
            return "phone"
        return None

    def send_welcome_email(self, to_email, user_name):
        try:
            subject = "Welcome to Raahi! Let's beat the Mumbai traffic together"
            body = f"""Hi {user_name}, we're thrilled to have you! Raahi is your new data-driven partner for smarter, smoother commutes across Mumbai.

What makes Raahi special:
- Real-time traffic analysis and route optimization
- Environmental impact tracking for your journeys
- Cost-effective transportation recommendations
- AQI-aware routing for healthier commutes

Getting started:
1. Enable location services for personalized routes
2. Plan your first trip to see Raahi in action
3. Track your environmental impact over time
4. Join our community of eco-conscious commuters

Need help? Reply to this email and we're here for you.

Best regards,
Team Raahi
{self.admin_email}"""

            msg = MIMEMultipart()
            msg["From"] = self.admin_email
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            if self.smtp_username and self.smtp_password:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                server.quit()
                return True

            print(f"Email credentials not configured. Would send to: {to_email}")
            return False
        except Exception as exc:
            print(f"Error sending email to {to_email}: {exc}")
            return False

    def send_welcome_sms(self, phone_number, user_name):
        try:
            formatted_phone = f"+91{phone_number}" if len(phone_number) == 10 else phone_number
            message = (
                f"Hi {user_name}, we're thrilled to have you! "
                "Raahi is your new data-driven partner for smarter, smoother commutes across Mumbai."
            )
            print(f"SMS would be sent to {formatted_phone}: {message}")
            return True
        except Exception as exc:
            print(f"Error sending SMS to {phone_number}: {exc}")
            return False

    def send_welcome_message(self, contact, user_name):
        contact_type = self.validate_email_or_phone(contact)
        if contact_type == "email":
            return self.send_welcome_email(contact, user_name)
        if contact_type == "phone":
            return self.send_welcome_sms(contact, user_name)

        print(f"Invalid contact format: {contact}")
        return False


notification_service = NotificationService()
