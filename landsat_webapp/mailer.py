import smtplib
from email.mime.text import MIMEText

# Globals
_SENDER = "reesaholics@gmail.com"
_PASSWORD = "oevh jnbv zlkh wcfo"


def send_email(subject, body, recipients, debuglevel=0):
    try:
        print("Creating MIMEText object...")
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = _SENDER
        msg["To"] = ", ".join(recipients)
        print("MIMEText object created successfully.")

        print("Connecting to SMTP server...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
            smtp_server.set_debuglevel(debuglevel)  # Enable debug output
            print("Logging in...")
            smtp_server.login(_SENDER, _PASSWORD)
            print("Logged in successfully.")

            print("Sending email...")
            smtp_server.sendmail(_SENDER, recipients, msg.as_string())
            print("Email sent successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    subject = "Email Subject"
    body = "This is the body of the text message"
    recipients = ["jeremiedevelops@gmail.com"]
    send_email(subject, body, recipients, debuglevel=1)
