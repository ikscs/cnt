import requests
import logging
from io import BytesIO

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class Service_exchange():
    def __init__(self):
        self.RECEPTION = 'http://face_reception:8000'
        self.RECEPTION_URL = f'{self.RECEPTION}/upload.json'
        self.EVENTS_URL = f'{self.RECEPTION}/events.json'
        self.OSD_URL = 'http://camera_pooling:8000/set_osd.json'

    def checkin(self, origin, title, filename, content, ts=None, origin_id=None):
        data = {'origin': origin, 'title': title}
        if ts:
            data['ts'] = ts
        files = {'f': (filename, BytesIO(content), 'application/octet-stream')}
        try:
            response = requests.post(self.RECEPTION_URL, data=data, files=files)
        except Exception as err:
            logging.error(str(err))

    def upload_events(self, cross_events):
        try:
            response = requests.post(self.EVENTS_URL, json=cross_events)
        except Exception as err:
            logging.error(str(err))

    def update_osd(self, point_id):
        try:
            response = requests.post(self.OSD_URL, data={'point_id': point_id})
        except Exception as err:
            logging.error(str(err))

if __name__ == "__main__":
    se = Service_exchange()

    with open('homer.jpg', 'rb') as f:
        content = f.read()
        se.checkin('user7@scs-analytics.com', 'Homer Simpson', 'homer', content)
