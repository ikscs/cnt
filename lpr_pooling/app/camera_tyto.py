import os
import requests
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from requests.auth import HTTPDigestAuth
import base64

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Camera():
    def __init__(self, credentials, max_results=200, timeout=10):
        self.host = credentials['host']
        self.proto = credentials['proto']
        self.port = credentials['port']
        self.user = credentials['user']
        self.password = credentials['password']
        self.chanel = credentials.get('chanel', 1)

        tz_default = 'Europe/Kyiv'
        tz = credentials.get('timezone', tz_default)
        try:
            self.tz = ZoneInfo(tz)
        except Exception as err:
            self.tz = ZoneInfo(tz_default)

        self.params = ''
        self.max_results = max_results

        self.url = f"{self.proto}://{self.host}:{self.port}/API"
        self.timeout = float(timeout)

        self.error_txt = 'Ok'
        self.req = self._check_session()
        self.is_connected = bool(self.req)

    def _check_session(self):
        url = f'{self.url}/Web/Login'
        session = requests.Session()
        session.verify = False
        session.auth = HTTPDigestAuth(self.user, self.password)

        try:
            response = session.post(url, timeout=self.timeout)
        except Exception as err:
            self.error_txt = str(err)
            print(str(err))
            return False

        if response.status_code != 200:
            self.error_txt = f'Response code: {response.status_code}'
            return False
        response.raise_for_status()

        session.headers.update({'X-csrftoken': response.headers['X-csrftoken'], 'Cookie': response.headers['Set-Cookie']})
        return session

    def request(self, point, data={}):
        if not self.is_connected:
            return False
        url = f'{self.url}/{point}'
        data = {"version": "1.0", "data": data}
        try:
            response = self.req.post(url, json=data, verify=False, timeout=self.timeout)
            if response.status_code != 200:
                return False
            return response.json()
        except Exception as err:
            print(str(err))
            return False
        return False

    def heart_beat(self):
        return self.request('Login/Heartbeat')

    def get_sysinfo(self):
        return self.request('SystemInfo/Base/Get')

    def get_event(self):
        return self.request('Event/Check')

    def get_snapshot(self):
        result = self.request('Snapshot/Get', {"channel": "CH1", "snapshot_resolution": "1920*1080"})
        if not result:
            return False
        try:
            return result["data"]["img_data"]
        except Exception as err:
            print(str(err))
            return False
        return False

    def make_action(self, action, plates=[], brands=[], owners=[]):
        actions = ['check', 'get', 'info', 'add', 'modify', 'remove', 'sync']
        if action not in actions:
            return {'success': False, 'description': f'Valid actions are: {", ".join(actions)}'}

        if action == 'check':
#            return self.is_connected
            point = 'Login/Heartbeat'
            data = {}

        elif action == 'get':
            point = 'AI/AddedPlates/GetId'
            plateinfo = []
            data = {"MsgId": None, "PlateInfo": plateinfo, "GrpId":[1],}

        elif action == 'add':
            point = 'AI/Plates/Add'
            if not brands: brands = ['' for e in plates]
            if not owners: owners = ['' for e in plates]
            plateinfo = [{"Id": k, "GrpId": 1, "CarBrand": brand, "Owner": owner} for k, brand, owner in zip(plates, brands, owners)]
            data = {"MsgId": None, "PlateInfo": plateinfo,}

        elif action == 'modify':
            point = 'AI/Plates/Modify'
            if not brands: brands = ['' for e in plates]
            if not owners: owners = ['' for e in plates]
            plateinfo = [{"Id": k, "GrpId": 1, "CarBrand": brand, "Owner": owner} for k, brand, owner in zip(plates, brands, owners)]
            data = {"MsgId": None, "PlateInfo": plateinfo,}

        elif action == 'remove':
            point = 'AI/Plates/Remove'
            plateinfo = [{"Id": e} for e in plates]
            data = {"MsgId": None, "PlateInfo": plateinfo,}

        elif action == 'sync':
            plates_in = set(plates)
            result = self.make_action('get')
            if not result:
                return False
            try:
                plates_ok = set(result['data']['PlatesId'])
            except Exception as err:
                print(str(err))
                return False

            result_del, result_add = 0, 0
            plates_del = plates_ok - plates_in
            if plates_del:
                result = self.make_action('remove', plates_del)
                if not result:
                    return False
                try:
                    result_del = result['data']['Count']
                except Exception as err:
                    print(str(err))
                    return False

            plates_add = plates_in - plates_ok
            if plates_add:
                result = self.make_action('add', plates_add)
                if not result:
                    return False
                try:
                    result_add = result['data']['Count']
                except Exception as err:
                    print(str(err))
                    return False

            return {'data': {'total': len(plates), 'add': result_add, 'remove': result_del}}

        elif action == 'info':
            result = self.make_action('get')
            if not result:
                return False
            try:
                plate_data_ids = [e for e in result['data']['PlatesId'] if e]
            except Exception as err:
                print(str(err))
                return False

            point = 'AI/AddedPlates/GetById'
            data = {"MsgId": None, "PlatesId": plate_data_ids,}

        return self.request(point, data)

    def load_plate_events(self, dt_start, dt_end):

        point = 'AI/SnapedObjects/SearchPlate'
        data = {"MsgId": None, "StartTime": self.dt_to_local(dt_start), "EndTime": self.dt_to_local(dt_end), "MaxErrorCharCnt": 3, "SortType": 0, "Engine": 0,}
        if not self.request(point, data):
            return False

        point = 'AI/SnapedObjects/GetByIndex'
        data = {"MsgId": None, "Engine": 0, "StartIndex": 0, "Count": self.max_results, "WithObjectImage": 0, "WithBackgroud": 0, "SimpleInfo": 1,}
        result = self.request(point, data)
        if not result:
            return False

        uuids = [rec['UUId'] for rec in result['data']['SnapedObjInfo']]

        point = 'AI/SnapedObjects/GetById'
        data = {"MsgId": None, "Engine": 0, "UUIds": uuids, "WithObjectImage": 0, "WithBackgroud": 0,}
        result = self.request(point, data)
        if not result:
            return False

        results = []
        try:
            for r in result['data']['SnapedObjInfo']:
                results.append([r["UUId"], self.int_to_dttz(r["StartTime"]), self.int_to_dttz(r["EndTime"]), r["GrpId"], r["Plate"] if r["Plate"] else None, r["MatchedPlate"] if r["MatchedPlate"] else None,])
        except Exception as err:
            print(result)
            print(str(err))

        point = 'AI/SnapedObjects/StopSearch'
        data = {"MsgId": None, "Engine": 0,}
        self.request(point, data)

        return results

    def int_to_dttz(self, utc):
        dt = datetime.fromtimestamp(utc)
        dt = dt.astimezone(timezone.utc)
        dt = dt.replace(tzinfo=self.tz)
        return dt

    def dt_to_local(self, dt):
        dt = dt.astimezone(self.tz)
        return f"{dt:%Y-%m-%d %H:%M:%S}"

    def get_by_uuid(self, uuid):
        point = 'AI/SnapedObjects/GetById'
        data = {"MsgId": None, "Engine": 0, "UUIds": [uuid], "WithObjectImage": 1, "WithBackgroud": 1,}
        result = self.request(point, data)
        if not result:
            return False

        try:
            return {'object': result['data']['SnapedObjInfo'][0]['ObjectImage'], 'background': result['data']['SnapedObjInfo'][0]['Background']}
        except Exception as err:
            return False


if __name__ == "__main__":
    from dotenv import dotenv_values
    credentials = dotenv_values('.env')

    camera = Camera(credentials)
    print(f'Connected: {camera.is_connected}')

    data = camera.make_action('get')
    print(data)
    print()

    data = camera.make_action('modify', ['QWERTY'], ['ABC'], ['DEF'])
    print(data)
    print()

    dt_end = datetime.now()
    dt_start = dt_end - timedelta(hours=1)

    results = camera.load_plate_events(dt_start, dt_end)
    for result in results:
        print(result)
