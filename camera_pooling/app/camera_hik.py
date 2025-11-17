from hikvisionapi import Client
from urllib.parse import urlparse, urlunparse, parse_qs
import xmltodict
import requests
from requests.auth import HTTPDigestAuth

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Camera(Client):
    def __init__(self, credentials):
        self.ip = credentials['host']
        self.proto = credentials['proto']
        self.port = credentials['port']
        self.user = credentials['user']
        self.password = credentials['password']
        self.chanel = credentials.get('chanel', 1)

        self.url = f"{self.proto}://{self.ip}:{self.port}"
        try:
            self.error_txt = 'Ok'
            super().__init__(self.url, self.user, self.password)
            self.is_connected = True
        except Exception as err:
            self.is_connected = False
            self.error_txt = str(err)
        self.media = dict()

    def change_url(self, url):
        parsed = urlparse(url)
        patched_url = urlunparse(parsed._replace(scheme=self.proto, netloc=f"{self.ip}:{self.port}"))
        return patched_url

    def get_snapshot(self):
        try:
            response = self.Streaming.channels[103].picture(method='get', type='opaque_data')
            response.raise_for_status()
        except Exception as err:
            print(str(err))
        return response.content

    def wrapped_request(self, method, url, data=None, is_xml=True):
        if not url.startswith('http'):
            url = f'{self.url}{url}'

        headers = {'Content-Type': 'application/xml'} if data else {}
        try:
            response = requests.request(nethod, url, data=data, auth=HTTPDigestAuth(self.user, self.password), headers=headers, verify=False)
            response.raise_for_status()
        except Exception as err:
            print(str(err))
            return None

        if not is_xml:
            return response

        try:
            result = xmltodict.parse(response.text)
        except Exception as err:
            return None
        return result

    def make_ISAPI_request(self, url, data):
        result = self.wrapped_request('POST', url, data)
        return result

    def make_ISAPI_PUT(self, url, data):
        result = self.wrapped_request('PUT', url, data)
        return result

    def make_ISAPI_GET(self, url):
        result = self.wrapped_request('GET', url)
        return result

    def get_media(self, url):
        response = self.wrapped_request('GET', url, is_xml=False)
        if not response:
            return b''
        return response.content

    def parse_media_url(self, url):
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        names = qs.get('name')
        self.media['name'] = names[0] if names else None
        sizes = qs.get('size')
        self.media['size'] = int(sizes[0]) if sizes else 0

    def set_osd(self, header, title, text):
        txt = f'{title}{text}'
        if header:
            txt = f'{header}\n{txt}'
        if not txt:
            return

        data = f'''<VideoOverlay><TextOverlayList><TextOverlay><id>1</id><enabled>true</enabled><displayText>{txt}</displayText></TextOverlay></TextOverlayList></VideoOverlay>'''
        url = '/ISAPI/System/Video/inputs/channels/1/overlays'
        result = self.make_ISAPI_PUT(url, data)

        return result
