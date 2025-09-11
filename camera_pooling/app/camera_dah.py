import json
import requests
import hashlib
from requests.auth import HTTPBasicAuth, HTTPDigestAuth

from urllib.parse import urlparse, urlunparse, parse_qs
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class DAH:
    field_map = {
      None: {
      },
      'detection': {
        'VideoStream': 'video_stream',
        'Channel': 'channel',
        'Type': 'f_type',
        'StartTime': 'start_time',
        'EndTime': 'end_time',
        'Disk': 'disk',
        'Partition': 'partition',
        'Cluster': 'cluster',
        'FilePath': 'file_path',
        'Length': 'length', 
        'Flags[0]': 'flags', 
        'Events[0]': 'events', 
        'CutLength': 'cut_length',
      },

      'detection2': {
        'Channel': 'channel',
        'Type': 'f_type',
        'StartTime': 'start_time',
        'EndTime': 'end_time',
        'EventTime': 'event_time',
        'Disk': 'disk',
        'Cluster': 'cluster',
        'Events[0]': 'events', 
        'CutLength': 'cut_length',
        'PicIndex': 'pic_index',
        'FilePath': 'file_path',
        'ObjectUrl[0]': 'object_url',
        'SummaryNew': 'summary',
      },

      'recognition': {
        'Channel': 'channel',
        'Type': 'f_type',
        'StartTime': 'start_time',
        'EndTime': 'end_time',
        'Disk': 'disk',
        'Cluster': 'cluster',
        'Events[0]': 'events', 
        'CutLength': 'cut_length',
        'PicIndex': 'pic_index',
        'EventTime': 'event_time',
        'ObjectUrl[0]': 'object0',
        'ObjectUrl[1]': 'object1',
        'SummaryNew': 'summary',
      },

      'crossline': {
        'Channel': 'channel',
        'Type': 'f_type',
        'StartTime': 'start_time',
        'EndTime': 'end_time',
        'EventTime': 'event_time',
        'Disk': 'disk',
        'Cluster': 'cluster',
        'Events[0]': 'events',
        'CutLength': 'cut_length',
        'PicIndex': 'pic_index',
        'FilePath': 'file_path',
        'Summary': 'summary',
      },

      'summary': {
        'Object.Image.FilePath': 'image_file_path',
        'Object.Image.Length': 'image_length',
        'Object.Sex': 'sex',
        'Object.Age': 'age',
        'Object.Emotion': 'emotion',
        'Object.Glasses': 'glasses',
        'Object.Attractive': 'attractive',
        'Object.Mask': 'mask',
        'Object.Beard': 'beard', 
        'Object.Mouth': 'mouth',
        'Object.Eye': 'eye',
        'Object.Nation': 'nation',
        'Object.Strabismus': 'strabismus',
        'Candidates[0].Person.Image[0].FilePath': 'person_image_file_path',
        'Candidates[0].Person.Image[0].Length': 'person_image_length',
        'Candidates[0].Person.Name': 'person_name',
        'Candidates[0].Person.Sex': 'person_sex',
        'Candidates[0].Person.Birthday': 'person_birthday',
        'Candidates[0].Person.Province': 'person_province',
        'Candidates[0].Person.Country': 'person_country',
        'Candidates[0].Person.City': 'person_city',
        'Candidates[0].Person.CertificateType': 'person_certificate_type',
        'Candidates[0].Person.ID': 'person_id',
        'Candidates[0].Person.GroupName': 'person_group_name',
        'Candidates[0].Person.UID': 'person_uid',
        'Candidates[0].Person.GroupID': 'person_group_id',
        'Candidates[0].Similarity': 'similarity',
        'IsGlobalScene': 'is_global_scene',
        'ImageInfo.Length': 'image_info_length',
        'Sequence': 'sequence',
        'BoundingBox[0]': 'bounding_box_0',
        'BoundingBox[1]': 'bounding_box_1',
        'BoundingBox[2]': 'bounding_box_2',
        'BoundingBox[3]': 'bounding_box_3',

        'ImageInfo.ImageType': 'image_info_image_type',
        'ObjectID': 'object_id',
        'TimeStamp.UTC': 'timestamp_utc',
        'TimeStamp.UTCMS': 'timestamp_utcms',
        'Sequence[0]': 'sequence0',
        'Sequence[1]': 'sequence1',
        'Sex': 'sex',
        'Age': 'age',
        'Glasses': 'glasses',
        'Emotion': 'emotion',
        'Attractive': 'attractive',
        'Mask': 'mask',
        'Beard': 'beard',
        'Mouth': 'mouth',
        'Eye': 'eye',
        'Nation': 'nation',
        'Strabismus': 'strabismus',

        'ImageInfo.FilePath': 'file_path',

        'Rule': 'rule',
        'ObjectType': 'object_type',
        'Action': 'action',

      },
    }

class Camera():
    def __init__(self, credentials, max_results=100, timeout=3):
        self.host = credentials['host']
        self.proto = credentials['proto']
        self.port = credentials['port']
        self.user = credentials['user']
        self.password = credentials['password']
        self.chanel = credentials['chanel']

        self.params = ''
        self.max_results = max_results

        self.url = f"{self.proto}://{self.host}:{self.port}/cgi-bin"
        self.timeout = float(timeout)

        self.field_map = DAH.field_map
        self.empty_rec = dict()
        for e in self.field_map:
            self.empty_rec[e] = {key: None for key in self.field_map[e].values()}

        try:
            self.error_txt = 'Ok'
            self.req = self._check_session()
            self.is_connected = self.login()
        except Exception as err:
            self.is_connected = False
            self.error_txt = str(err)

    def _check_session(self):
        url = f'{self.url}/magicBox.cgi?action=getHardwareVersion'
        session = requests.Session()
        session.verify = False
        session.auth = HTTPBasicAuth(self.user, self.password)
        response = session.get(url)
        if response.status_code == 401:
            session.auth = HTTPDigestAuth(self.user, self.password)
            response = session.get(url)
        response.raise_for_status()
        return session

    def login(self):
        """Dahua RPC login.
        Thanks: https://gist.github.com/avelardi/1338d9d7be0344ab7f4280618930cd0d
        """
        url = f'{self.proto}://{self.host}:{self.port}/RPC2_Login'

        # login1: get session, realm & random for real login
        method = "global.login"
        params = {'userName': self.user, 'password': "", 'clientType': "Dahua3.0-Web3.0"}
        data = {'method': method, 'id': 1, 'params': params}
        result = self.req.post(url, json=data)
        r = result.json()

        self.session_id = r['session']
        realm = r['params']['realm']
        random = r['params']['random']

        # Password encryption algorithm
        # Reversed from rpcCore.getAuthByType
        pwd_phrase = self.user + ":" + realm + ":" + self.password
        if isinstance(pwd_phrase, str):
            pwd_phrase = pwd_phrase.encode('utf-8')
        pwd_hash = hashlib.md5(pwd_phrase).hexdigest().upper()
        pass_phrase = self.user + ':' + random + ':' + pwd_hash
        if isinstance(pass_phrase, str):
            pass_phrase = pass_phrase.encode('utf-8')
        pass_hash = hashlib.md5(pass_phrase).hexdigest().upper()

        # login2: the real login
        params = {'userName': self.user, 'password': pass_hash, 'clientType': "Dahua3.0-Web3.0", 'authorityType': "Default", 'passwordType': "Default"}
        data = {'method': method, 'id': 2, 'params': params, 'session': self.session_id}
        result = self.req.post(url, json=data)
        r = result.json()

        return r['result']

    def get_media(self, media_url):
        if 'IntelliStorage' in media_url:
            url = f"{self.proto}://{self.host}:{self.port}{media_url}"
        else:
            url = f"{self.proto}://{self.host}:{self.port}/cgi-bin/RPC_Loadfile{media_url}"
        response = self.req.request('GET', url, timeout=self.timeout)
        return response.content

    def set_osd(self, header, title, text):
        return None

    def exec(self, q):
        url = f'{self.url}/{q}'
        response = self.req.request('GET', url, timeout=self.timeout)
        return response.status_code

    def query(self, q, mode=None):
        #'''
        url = f'{self.url}/{q}'
        response = self.req.request('GET', url, timeout=self.timeout)

        if response.status_code != 200:
            print('Error status code', response.status_code, response.text)
            return response.status_code

        if response.headers.get('Content-type') != 'text/plain;charset=utf-8':
            print('Wrong content')
            print(response.text)
            return 0

        t = response.text

        data = [e.strip() for e in t.split('\n') if e]

        self.result = dict()
        self.items = []

        for e in data:
            rec = e.split('=', 1)
            if len(rec) == 1:
                self.result[rec[0]] = None
            elif len(rec) == 2:
                val = rec[1].strip()
                if rec[0].startswith('items['):
                    idx = 0
                    k = 6
                    while rec[0][k] != ']':
                        idx = idx*10 + int(rec[0][k])
                        k += 1
                    if len(self.items) == idx:
                        self.items.append(self.empty_rec[mode].copy())
                        if mode in ('recognition', 'detection2', 'crossline'):
                           self.items[idx]['summary'] = dict()
                    key_in = rec[0][k+2:].strip()
                    key_out = self.field_map[mode].get(key_in)
                    if key_out:
                        self.items[idx][key_out] = val
                    elif key_in.startswith('SummaryNew[0].Value.'):
                        key_in = key_in[20:]
                        key_out = self.field_map['summary'].get(key_in)
                        if key_out:
                            self.items[idx]['summary'][key_out] = val
                    elif key_in.startswith('Summary.IVS.'):
                        key_in = key_in[12:]
                        key_out = self.field_map['summary'].get(key_in)
                        if key_out:
                            self.items[idx]['summary'][key_out] = val

                self.result[rec[0]] = val

        return 200

    def open_factory(self):
        self.query("mediaFileFind.cgi?action=factory.create")
        self.obj = self.result['result']
        self.params = f"object={self.obj}&condition.Channel={self.chanel}"

    def close_factory(self):
        self.exec(f"mediaFileFind.cgi?action=close&object={self.obj}")
        self.exec(f"mediaFileFind.cgi?action=destroy&object={self.obj}")

    def get_dt(self):
        start_dt = '2025-08-15 17:20:00'
        end_dt = '2025-08-16 00:00:00'
        return start_dt, end_dt

    def get_detection(self, start_dt, end_dt):
        params = f"{self.params}&condition.StartTime={start_dt}&condition.EndTime={end_dt}&condition.Flags[0]=Event&condition.Events[0]=FaceRecognition"

        return_code = self.query(f"mediaFileFind.cgi?action=findFile&{params}")
        if return_code == 200:
            params = f"{self.params}&count={self.max_results}"
            return_code = self.query(f"mediaFileFind.cgi?action=findNextFile&{params}", 'detection')

        return return_code

    def get_recognition(self, start_dt, end_dt):
        params = f"{self.params}&condition.Types[0]=jpg&condition.Events[0]=FaceRecognition"
        params = f"{params}&condition.DB.FaceRecognitionRecordFilter.StartTime={start_dt}&condition.DB.FaceRecognitionRecordFilter.EndTime={end_dt}"

        return_code = self.query(f"mediaFileFind.cgi?action=findFile&{params}")
        if return_code == 200:
            params = f"{self.params}&count={self.max_results}"
            return_code = self.query(f"mediaFileFind.cgi?action=findNextFile&{params}", 'recognition')

        return return_code

    def get_detection2(self, start_dt, end_dt):
        params = f"{self.params}&condition.StartTime={start_dt}&condition.EndTime={end_dt}&condition.Flags[0]=Event&condition.Types[0]=jpg"
        params = f"{params}&condition.Events[0]=FaceDetection&condition.DB.FaceDetectionRecordFilter.Age[0]=1&condition.DB.FaceDetectionRecordFilter.Age[1]=100"

        return_code = self.query(f"mediaFileFind.cgi?action=findFile&{params}")
        if return_code == 200:
            params = f"{self.params}&count={self.max_results}"
            return_code = self.query(f"mediaFileFind.cgi?action=findNextFile&{params}", 'detection')

        return return_code

    def get_crossline(self, start_dt, end_dt):
        params = f"{self.params}&condition.StartTime={start_dt}&condition.EndTime={end_dt}&condition.Types[0]=jpg&condition.DB.IVS.Rule=CrossLineDetection"

        return_code = self.query(f"mediaFileFind.cgi?action=findFile&{params}")
        if return_code == 200:
            params = f"{self.params}&count={self.max_results}"
            return_code = self.query(f"mediaFileFind.cgi?action=findNextFile&{params}", 'crossline')

        return return_code


if __name__ == "__main__":
    from dotenv import dotenv_values
#    credentials = dotenv_values('.env_dah')
    credentials = dotenv_values('.env_dah_camera')
    camera = Camera(credentials, max_results=2)

    if not camera.is_connected:
        print(camera.error_txt)

    camera.open_factory()

    start_dt, end_dt = camera.get_dt()

    res = camera.get_crossline(start_dt, end_dt)

    camera.close_factory()

    for e in camera.items:
        content = camera.get_media(e['file_path'])

        if '=' in e['file_path']:
            file_name = e['file_path'].split('=')[-1]
        elif '.dav' in e['file_path']:
            file_name = f"{e['start_time']}__{e['end_time']}.dav".replace(' ', '_').replace(':', '').replace('-', '')
        elif '.jpg' in e['file_path']:
            file_name = f"{e['start_time']}.jpg".replace(' ', '_').replace(':', '').replace('-', '')
        else:
            file_name = e['file_path'].replace('/', '_')

        with open(file_name, 'wb') as fp:
            fp.write(content)
