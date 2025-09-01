import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import json

class Sender:
    def __init__(self, cfg):
        self.sender_email = cfg['mta_origin']
        self.recipient = cfg['recipient']
        self.smtp_server = cfg['SMTP']
        self.smtp_port = cfg['PORT']
        self.smtp_user = cfg['mta_login']
        self.smtp_password = cfg['mta_password']
        self.context = ssl._create_unverified_context()

        self.start_tls = cfg['STARTTLS']
        self.encryption = cfg['encryption']# not used

    def send_email(self, subject: str, body: str, html: str=None, attachment_data: bytes=None, attachment_name: str=None):
        if not bytes:
            return

        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = self.recipient
        msg['Subject'] = subject

        # Attach email body
        msg.attach(MIMEText(body, 'plain'))
        if html:
            msg.attach(MIMEText(html, 'html'))

        # Attach in-memory file data if provided
        if attachment_data and attachment_name:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment_data)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{attachment_name}"')
            msg.attach(part)

        # Send the email
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.ehlo()
                if self.start_tls:
                    server.starttls(context=self.context)
                    server.ehlo()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.sender_email, self.recipient, msg.as_string())
            #print("[Success] Email sent successfully.")
        except Exception as e:
            print(f"[Error] Failed to send email: {e}")

def get_email_cfg(cursor):
    sql_email = "SELECT value FROM param WHERE name='smtp_email'"
    cursor.execute(sql_email)
    row = cursor.fetchone()
    if not row:
        return None
    try:
         result = json.loads(row[0]['value'])
    except Exception as err:
        print(err)
        return None

    email_cfg = dict()
    try:
        email_cfg['mta_password'] = result['psw']
        email_cfg['mta_origin'] = result['sender']
        email_cfg['STARTTLS'] = result['SSL_TLS']
        email_cfg['PORT'] = result['smtp_port']
        email_cfg['SMTP'] = result['smtp_server']
        email_cfg['recipient'] = None
        email_cfg['mta_login'] = result['sender'].split('>')[0].split('<')[1]
        email_cfg['encryption'] = None
    except Exception as err:
        print(err)
        return None

    return email_cfg

if __name__ == "__main__":
    from dotenv import dotenv_values
    env = '.env_sender'
    cfg = dotenv_values(env)
    sender = Sender(cfg)

    image_path = "image1.jpg"
    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
        image_name = image_path.split("/")[-1]

        subject = "Test Email with In-Memory Attachment"
        body = "Hello, this is a test email with an image loaded in memory."

        sender.send_email(subject, body, attachment_data=image_data, attachment_name=image_name)

    except FileNotFoundError:
        print(f"[Error] File '{image_path}' not found.")
