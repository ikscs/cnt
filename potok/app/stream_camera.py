import os
import onvif
from onvif import ONVIFService
from zeep.transports import Transport
import requests
from requests import Session
from urllib.parse import urlunparse, urlparse

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from requests.auth import HTTPDigestAuth
from threading import Lock

class streamCamera():
    _screenshot_lock = Lock()
    def __init__(self, cfg):
        self.cfg = cfg

        self.auth = HTTPDigestAuth(self.cfg['user'], self.cfg['password'])

        self.create_manual_onvif_services()

        profiles = self.media_service.GetProfiles()

        self.token1 = profiles[0].token
        self.token2 = profiles[1].token

        snapshot_uri = self.media_service.GetSnapshotUri({'ProfileToken': self.token1})
        self.snapshot_uri = self.patch_uri(snapshot_uri.Uri, self.cfg['host'], self.cfg['http_port'], force_scheme=self.cfg['proto'])

        self.rtsp_uri1 = self.get_rtsp_uri(self.token1)
        self.rtsp_uri2 = self.get_rtsp_uri(self.token2)

    def get_rtsp_uri(self, token):
        uri = self.media_service.GetStreamUri({'StreamSetup': {'Stream': 'RTP-Unicast', 'Transport': {'Protocol': 'RTSP'}}, 'ProfileToken': token})
        rtsp_uri = self.patch_uri(uri.Uri, self.cfg['host'], self.cfg['rtsp_port'], force_scheme=None, username=self.cfg['user'], password=self.cfg['password'])
        return rtsp_uri

    def patch_uri(self, original_uri, public_host, public_port=None, force_scheme=None, username=None, password=None):
        parsed = urlparse(original_uri)
        scheme = force_scheme if force_scheme else parsed.scheme

        # Construct userinfo if username and/or password are given
        userinfo = ''
        if username:
            userinfo = username
            if password:
                userinfo += f":{password}"
            userinfo += '@'

        netloc = f"{userinfo}{public_host}"
        if public_port:
            netloc += f":{public_port}"

        return urlunparse(parsed._replace(scheme=scheme, netloc=netloc))

    def create_manual_onvif_services(self):
        self.base_url = f"{self.cfg['proto']}://{self.cfg['host']}:{self.cfg['http_port']}/onvif"

        # Transport with timeout
        session = Session()
        session.verify = False
        session.timeout = 5
        transport = Transport(session=session)

        onvif_base_path = os.path.dirname(onvif.__file__) #Get the directory where the onvif module is installed
        parent_dir = os.path.dirname(onvif_base_path) #move one level up
        self.wsdl_path = os.path.join(parent_dir, 'wsdl')

        # Create device management service
        self.device_service = ONVIFService(
            f"{self.base_url}/device_service",
            self.cfg['user'],
            self.cfg['password'],
            f"{self.wsdl_path}/devicemgmt.wsdl",
            transport=transport,
            binding_name="{http://www.onvif.org/ver10/device/wsdl}DeviceBinding"
        )

        # Get capabilities from device
        capabilities = self.device_service.GetCapabilities()
        media_url = capabilities.Media.XAddr

        # Patch media URL to use external IP, port and scheme
        self.media_url = self.patch_uri(media_url, self.cfg['host'], self.cfg['http_port'], force_scheme=self.cfg['proto'])

        # Create media service
        self.media_service = ONVIFService(
            self.media_url,
            self.cfg['user'],
            self.cfg['password'],
            f"{self.wsdl_path}/media.wsdl",
            transport=transport,
            binding_name="{http://www.onvif.org/ver10/media/wsdl}MediaBinding"
        )

    def get_snapshoot(self):
        if not self._screenshot_lock.acquire(blocking=False):
            return
        content = None
        try:
            response = requests.request("GET", self.snapshot_uri, auth=self.auth, verify=False)
            if response.status_code == 200:
                content = response.content
        finally:
            self._screenshot_lock.release()

        return content

if __name__ == "__main__":
    from dotenv import dotenv_values

#    env = '.env_114'
    env = '.env_sezon1'
#    env = '.env_sezon4'
#    env = '.env_84'
    cfg = dotenv_values(env)

    camera = streamCamera(cfg)
    print("✅ RTSP URI:", camera.rtsp_uri1)
    print("✅ RTSP URI:", camera.rtsp_uri2)
    print("✅ Snapshot URI:", camera.snapshot_uri)

