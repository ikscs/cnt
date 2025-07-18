import requests
import logging
from io import BytesIO

import os
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class Service_exchange():
    def __init__(self):
        self.RECEPTION = 'http://face_reception:8000'
        self.RECEPTION_URL = f'{self.RECEPTION}/upload.json'
        self.EVENTS_URL = f'{self.RECEPTION}/events.json'
        self.OSD_URL = 'http://camera_pooling:8000/set_osd.json'
        self.KV_DB_URL = 'http://kv_db:5000'

        self.service = {
            'processor': 'http://localhost:8000/processor.json',
            'similarity':  'http://localhost:8000/similarity.json',
            'demography': 'http://localhost:8000/demography.json',
        }

    def checkin(self, origin, origin_id, title, filename, content, ts=None):
        data = {'origin': origin, 'origin_id': origin_id, 'title': title}
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

    def get_img(self, uuid):
        try:
            response = requests.get(f"{self.KV_DB_URL}/get/{uuid}")
            response.raise_for_status()
            return response.content
        except Exception as err:
            logging.error(str(err))
            return None

    def set_img(self, uuid, data):
        headers = {"Content-Type": "application/octet-stream"}
        try:
            response = requests.post(f"{self.KV_DB_URL}/set/{uuid}", headers=headers, data=data)
            response.raise_for_status()
            return response.content
        except Exception as err:
            logging.error(str(err))
            return None

    def post_engine(self, url, data, files):
        try:
            response = requests.post(url, data=data, files=files)
            response.raise_for_status()
            return response.json()
        except Exception as err:
            logging.error(str(err))
            return None

    def launch_service(self, service):
        url = self.service[service]
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as err:
            logging.error(str(err))
            return None

if __name__ == "__main__":
    se = Service_exchange()

    with open('homer.jpg', 'rb') as f:
        content = f.read()
        se.checkin('user7@scs-analytics.com', 7, 'Homer Simpson', 'homer', content)
