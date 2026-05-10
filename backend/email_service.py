import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

CONFIG_FILE = "config.json"

def get_smtp_config():
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, "r") as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError:
            return None
            
        host = config.get("smtp_host")
        if not host:
            return None
            
        return {
            "host": host,
            "port": config.get("smtp_port", 587),
            "user": config.get("smtp_user", ""),
            "password": config.get("smtp_password", ""),
            "tls": config.get("smtp_tls", True)
        }

def send_issue_email(subject: str, body: str, recipients: list[str]):
    config = get_smtp_config()
    if not config or not config["host"]:
        return False
        
    if not recipients:
        return False
        
    msg = MIMEMultipart()
    msg["From"] = config["user"] or "tracker@noreply.com"
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))
    
    try:
        server = smtplib.SMTP(config["host"], config["port"])
        if config["tls"]:
            server.starttls()
        if config["user"] and config["password"]:
            server.login(config["user"], config["password"])
        server.sendmail(msg["From"], recipients, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def notify_issue_update(issue_title: str, action: str, details: str, recipient_emails: list[str]):
    """Helper function to format and send an issue notification."""
    valid_emails = [email for email in recipient_emails if email]
    if not valid_emails:
        return False
        
    subject = f"Tracker Issue Notification: {issue_title}"
    body = f"""
    <html>
        <body>
            <h2>Tracker Issue Update</h2>
            <p><strong>Issue:</strong> {issue_title}</p>
            <p><strong>Action:</strong> {action}</p>
            <p>{details}</p>
        </body>
    </html>
    """
    return send_issue_email(subject, body, valid_emails)
