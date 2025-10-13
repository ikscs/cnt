#!/usr/bin/python3
import sys
import email
import email.header
from email.utils import getaddresses

import requests
from io import BytesIO

url = 'http://face_reception:8000/upload.json'

def decode_subject(s):
    part, encoding = email.header.decode_header(s)[0]
    if isinstance(part, bytes):
        decoded_string = part.decode(encoding if encoding else 'utf-8')
        decoded_string = decoded_string.strip('\u0000')
    else:
        decoded_string = part
    return decoded_string

def decode_address(s):
    addresses = getaddresses([s])
    if addresses:
        for name, email in addresses:
            break
    else:
        email = None
    return email

def process_email(email_bytes):
    msg = email.message_from_bytes(email_bytes)
    data = {'origin': decode_address(msg['From']), 'title': decode_subject(msg['Subject'])}

    attachments = msg.get_payload()

    for attachment in attachments:
        try:
            fnam = attachment.get_filename()
            if not fnam:
                continue
            if fnam and fnam.lower().startswith('=?utf-8?b?'):
                fnam = decode_subject(fnam)

            ext = fnam.rsplit('.')[-1]
            if ext.lower() not in ('png', 'bmp', 'jpg', 'jpeg', 'webp', 'gif'):
                continue

            f = attachment.get_payload(decode=True,)
            files = {'f': (fnam, BytesIO(f), 'application/octet-stream')}
            response = requests.post(url, data=data, files=files)

        except Exception as err:
            print(err)

if __name__ == "__main__":
    email_bytes = sys.stdin.buffer.read()

#    from datetime import datetime
#    ts = datetime.timestamp(datetime.now())
#    with open(f"/tmp/{ts}.eml", "wb") as binary_file:
#        binary_file.write(email_bytes)

    process_email(email_bytes)
