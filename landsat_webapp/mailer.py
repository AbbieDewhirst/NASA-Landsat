import smtplib
from email.mime.text import MIMEText

subject = "Email Subject"
body = "This is the body of the text message"
sender = "reesaholics@gmail.com"
recipients = ["mat_p1999@hotmail.com"]
password = "oevh jnbv zlkh wcfo"


def send_email(subject, body, sender, recipients, password):
    try:
        print("Creating MIMEText object...")
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = ", ".join(recipients)
        print("MIMEText object created successfully.")

        print("Connecting to SMTP server...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
            smtp_server.set_debuglevel(1)  # Enable debug output
            print("Logging in...")
            smtp_server.login(sender, password)
            print("Logged in successfully.")

            print("Sending email...")
            smtp_server.sendmail(sender, recipients, msg.as_string())
            print("Email sent successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")


send_email(subject, body, sender, recipients, password)
