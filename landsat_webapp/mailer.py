import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

# Mailjet SMTP server configuration
SMTP_SERVER = os.environ.get("SMTP_SERVER")
SMTP_PORT = os.environ.get("SMTP_PORT")
SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")

# Email details
sender_email = SENDER_EMAIL
recipient_email = input("Enter an email address >").strip()
subject = input("Enter a subject >").strip()
body = input("Enter a body >").strip()

# Create the email message
msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = recipient_email
msg["Subject"] = subject
msg.attach(MIMEText(body, "plain"))

# Connect to the Mailjet SMTP server and send the email
try:
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()  # Secure the connection
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    server.sendmail(sender_email, recipient_email, msg.as_string())
    print("Email sent successfully")
except Exception as e:
    print(f"Failed to send email: {e}")
finally:
    server.quit()
