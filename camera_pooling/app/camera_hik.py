from hikvisionapi import Client
from urllib.parse import urlparse, urlunparse, parse_qs
import xmltodict
import requests
from requests.auth import HTTPDigestAuth

class Camera(Client):
    def __init__(self, credentials):
        self.ip = credentials['host']
        self.proto = credentials['proto']
        self.port = credentials['port']
        self.user = credentials['user']
        self.password = credentials['password']
        self.url = f"{self.proto}://{self.ip}:{self.port}"
        try:
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
        response = self.Streaming.channels[103].picture(method='get', type='opaque_data')
        return response.content

    def make_ISAPI_request(self, url, data):
        response = requests.post(f'{self.url}{url}', data=data, auth=HTTPDigestAuth(self.user, self.password), headers={'Content-Type': 'application/xml'}, verify=False)
        result = xmltodict.parse(response.text)
        return result

    def make_ISAPI_PUT(self, url, data):
        response = requests.put(f'{self.url}{url}', data=data, auth=HTTPDigestAuth(self.user, self.password), headers={'Content-Type': 'application/xml'}, verify=False)
        result = xmltodict.parse(response.text)
        return result

    def get_media(self, url):
        response = requests.request("GET", url, auth=HTTPDigestAuth(self.user, self.password), verify=False)
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
