from datetime import datetime, timedelta
from service_exchange import Service_exchange
import logging

from camera_hik import Camera
import uuid

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def get_dict_value(src, *keys):
    result = src
    for key in keys:
        result = result.get(key)
        if result == None:
            break
    return result

def hik_runner(credentials, origin, origin_id, last_dt, params):
    logging.info(f"Running periodic task for {origin} from {last_dt}")
    se = Service_exchange()

    camera = Camera(credentials)
    if not camera.is_connected:
        logging.error(camera.error_txt)
        return 0, None

    start_time = (last_dt + timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

    now = datetime.now()
    end_time = (now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

    max_results = 50

    data = f'''
<CMSearchDescription>
<searchID>{uuid.uuid4()}</searchID>
<trackIDList><trackID>103</trackID></trackIDList>
<timeSpanList>
<timeSpan><startTime>{start_time}</startTime>
<endTime>{end_time}</endTime>
</timeSpan>
</timeSpanList>
<contentTypeList><contentType>metadata</contentType>
</contentTypeList><maxResults>{max_results}</maxResults>
<searchResultPostion>0</searchResultPostion>
<metadataList>
<metadataDescriptor>//recordType.meta.std-cgi.com/{params['event']}
</metadataDescriptor>
</metadataList></CMSearchDescription>
'''

    end_time = now #Default end date

    res = camera.make_ISAPI_request('/ISAPI/ContentMgmt/search', data=data)
    mtl = get_dict_value(res, 'CMSearchResult', 'matchList')

    if not mtl:
        return 0, end_time

    result = None
    for k, result in mtl.items():
        break

    if not result:
        return 0, end_time

    cnt = 0
    cross_events = []
    for n, e in enumerate(result):
        if isinstance(e, str):
            break
        url = get_dict_value(e, 'mediaSegmentDescriptor', 'playbackURI')
        if not url:
            continue

        url = camera.change_url(url)

        camera.parse_media_url(url)

        try:
            title = e['timeSpan']['startTime']
            ts = datetime.fromisoformat(title[:-1])
        except Exception as e:
            continue

        try:
            end_time = e['timeSpan']['endTime']
            end_time = datetime.fromisoformat(end_time[:-1])
        except Exception as e:
            continue

        if 'lineCrossImage' in camera.media['name']:
            prefix, name = camera.media['name'].split('@')
            cross_events.append({'origin': origin, 'origin_id': origin_id, 'ts': str(ts), 'prefix': prefix, 'name': name})

        if 'min_size' in params:
            if camera.media['size'] < params['min_size']:
                continue
        if 'max_size' in params:
            if camera.media['size'] > params['max_size']:
                continue

        if 'file_mask' in params:
            if params['file_mask'] not in camera.media['name']:
                continue

        content = b''
        retry = 3
        while (len(content) < params['min_size']) and (retry > 0):
            content = camera.get_media(url)
            retry -= 1
        if len(content) < params['min_size']:
            continue

        se.checkin(origin, origin_id, title, camera.media['name'], content, ts)

        cnt += 1

    if cross_events:
        se.upload_events(cross_events)

    logging.info(f"Parsed {cnt}/{n+1}. Last event {end_time}")
    return n + 1, end_time

if __name__ == "__main__":
    import os
    from dotenv import dotenv_values

    credentials = dotenv_values('.env_hik')
    origin = 'sezon_FF_1'
    origin_id = 19
    last_dt = datetime.now() + timedelta(seconds=-36000)

    params = {"event": "LineDetection", "max_size": 1000000, "min_size": 500000, "file_mask": "lineCrossCap"}

    count, end_time = hik_runner(credentials, origin, origin_id, last_dt, params)
    print(count, end_time)
