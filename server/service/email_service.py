import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from server.util.config import getConfig


class EmailService:
    config = getConfig()
    GMAIL_ACC = config.get_gmail_acc()
    GMAIL_PW = config.get_gmail_pw()

    def send_invite(self, to_emails, response, name):
        print("Sending email")
        msg = MIMEMultipart()
        msg["From"] = self.GMAIL_ACC
        if isinstance(to_emails, list):
            msg["To"] = ", ".join(to_emails)
        else:
            msg["To"] = to_emails
        msg["Subject"] = response.subject

        msg.attach(MIMEText(f"{response.body}", "plain"))

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.set_debuglevel(1)
                server.starttls()
                server.login(self.GMAIL_ACC, self.GMAIL_PW)
                server.send_message(msg)
            print("Email sent!")
        except smtplib.SMTPAuthenticationError:
            print("Authentication failed: check email/password or use App Password")
        except Exception as e:
            print("Failed to send email:", e)
