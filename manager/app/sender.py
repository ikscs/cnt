import smtplib
import ssl
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
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

    def send_email(self, subject, body, html=None, attachment_data=None, attachment_name=None):
        if (body or html) and attachment_data:
            msg = MIMEMultipart()
            msg.attach(MIMEText(html if html else body, _subtype='html' if html else 'text', _charset='utf-8'))
        else:
            msg = MIMEText(html if html else body, _subtype='html' if html else 'text', _charset='utf-8')

        msg['From'] = self.sender_email
        msg['To'] = self.recipient
        msg['Subject'] = subject

        if not isinstance(attachment_data, (list, tuple)):
            attachment_data = [attachment_data,]
            attachment_name = [attachment_name,]

        n = 1
        for att_data, att_name in zip(attachment_data, attachment_name):
            if not (att_data and att_name):
                continue
            ext = att_name.split('.')[-1].lower()

            ctype, encoding = mimetypes.guess_type(att_name)
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)

            if maintype == 'image':
                part = MIMEImage(att_data, _subtype=subtype)
            else:
                part = MIMEBase(maintype, subtype)
                part.set_payload(att_data)
                encoders.encode_base64(part)

            part.add_header('Content-Disposition', 'attachment', filename=att_name)
            part.add_header('Content-ID', f'<att{n}>')
            n += 1
            msg.attach(part)

#        print(msg)
#        return
#        die

        # Send the email
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.ehlo()
                if self.start_tls:
                    server.starttls(context=self.context)
                    server.ehlo()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
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

    subject = "Test Email with In-Memory Attachment"
    body = "Hello, simple text."
    html = "<h1>Hello</h1>"

    if False:
        # Simple mail
        sender.send_email(subject, body=None, html=html)
        #sender.send_email(subject, body=body)

    if False:
        # Image mail
        image_path = "image1.jpg"
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
            image_name = image_path.split("/")[-1]
        except FileNotFoundError:
            print(f"[Error] File '{image_path}' not found.")
        sender.send_email(subject, body=body, html=None, attachment_data=image_data, attachment_name=image_name)

    if False:
        from xlsx_report import mk_xlsx_report
        # Xlsx mail
        data = [
            {"Name": "Alice", "Age": 30, "City": "New York"},
            {"Name": "Bob", "Age": 25, "City": "San Francisco"},
            {"Name": "Charlie", "Age": 35, "City": "Chicago"},
        ]
        xlsx_data = mk_xlsx_report(subject, data)
        sender.send_email(subject, body=None, html=html, attachment_data=xlsx_data, attachment_name=f'{subject}.xlsx')

    if True:
        # Combo mail
        attachment_data = []
        attachment_name = []

        image_path = "image1.jpg"
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
            image_name = image_path.split("/")[-1]
        except FileNotFoundError:
            print(f"[Error] File '{image_path}' not found.")
        attachment_data.append(image_data)
        attachment_name.append(image_name)

        from xlsx_report import mk_xlsx_report
        # Xlsx mail
        data = [
            {"Name": "Alice", "Age": 30, "City": "New York"},
            {"Name": "Bob", "Age": 25, "City": "San Francisco"},
            {"Name": "Charlie", "Age": 35, "City": "Chicago"},
        ]
        xlsx_data = mk_xlsx_report(subject, data)
        attachment_data.append(xlsx_data)
        attachment_name.append(f'{subject}.xlsx')

        sender.send_email(subject, body=None, html=html, attachment_data=attachment_data, attachment_name=attachment_name)
