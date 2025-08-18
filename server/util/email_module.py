import smtplib
from email.mime.text import MIMEText
import logging

class EmailModule:
    def __init__(self, smtp_server, smtp_port, username, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

    def send_email(self, recipient, subject, body, is_html=False):
        """
        Send an email.
        :param recipient: Email recipient.
        :param subject: Email subject.
        :param body: Email body.
        :param is_html: Whether the email body is HTML.
        """
        try:
            msg = MIMEText(body, "html" if is_html else "plain")
            msg['Subject'] = subject
            msg['From'] = self.username
            msg['To'] = recipient

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.username, recipient, msg.as_string())

            logging.info(f"Email sent to {recipient} with subject: {subject}")
        except Exception as e:
            logging.error(f"Failed to send email to {recipient}: {e}")

# Example usage
if __name__ == "__main__":
    email_module = EmailModule("smtp.example.com", 587, "user@example.com", "password")
    email_module.send_email("recipient@example.com", "Negotiation Email", "<p>Please review the attached rider clauses.</p>", is_html=True)
