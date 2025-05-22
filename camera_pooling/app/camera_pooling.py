import os
import time
from datetime import datetime, timedelta
import requests
from io import BytesIO
import logging
import psycopg2

#from dotenv import load_dotenv

from camera_hik import Camera
import uuid

RECEPTION = 'http://face_reception:8000'
RECEPTION_URL = f'{RECEPTION}/upload.json'
EVENTS_URL = f'{RECEPTION}/events.json'
OSD_URL = 'http://localhost:8000/set_osd.json'

ORIGIN_PROTOCOL = 'ISAPI'
ORIGIN_VENDOR = 'Hikvision'

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def get_dict_value(src, *keys):
    result = src
    for key in keys:
        result = result.get(key)
        if result == None:
            break
    return result

def run_job(credentials, origin, last_dt, params):
    logging.info(f"Running periodic task for {origin} from {last_dt}")
    camera = Camera(credentials)
    if not camera.is_connected:
        logging.error(camera.error_txt)
        return 0, None

    start_time = (last_dt+timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

    now = datetime.now()
    end_time = (now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

    max_results = 50

    data = f"""
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
"""

    end_time = now #Default end date

    res = camera.make_ISAPI_request('/ISAPI/ContentMgmt/search', data=data)
    #mtl = res['CMSearchResult']['matchList']
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
        #url = e['mediaSegmentDescriptor']['playbackURI']
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
            cross_events.append({'origin': origin, 'ts': str(ts), 'prefix': prefix, 'name': name})

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

#        image_name = f"{origin}_{n}.jpg"
#        with open(image_name, 'wb') as fp:
#            fp.write(content)

        data = {'origin': origin, 'title': title, 'ts': ts}
        files = {'f': (camera.media['name'], BytesIO(content), 'application/octet-stream')}
        response = requests.post(RECEPTION_URL, data=data, files=files)

        cnt += 1

    if cross_events:
        try:
            response = requests.post(EVENTS_URL, json=cross_events)
#            logging.info(f'Ok {response.status_code}')
        except Exception as e:
            logging.error(str(e))

    logging.info(f"Parsed {cnt}/{n+1}. Last event {end_time}")
    return n+1, end_time

def main():
    logging.info("Start service")
    time_sleep_min = 10
    time_sleep_max = 10*60

    schema = os.environ['POSTGRES_SCHEMA']

    sql_jobs = f"""
SELECT o.point_id, o.id, o.origin, o.credentials, s.poling_period_s, t.params
FROM {schema}.origin o
LEFT JOIN {schema}.origin_schedule s using(id)
LEFT JOIN {schema}.origin_type t using(origin_type_id)
WHERE
t.protocol = '{ORIGIN_PROTOCOL}'
AND t.vendor = '{ORIGIN_VENDOR}'
AND o.is_enabled
AND s.is_enabled
AND CURRENT_TIME between start_time AND end_time
AND NOW() >= next_dt
ORDER BY next_dt ASC
LIMIT 1
"""

#    sql_last_dt = f"SELECT ts FROM {schema}.incoming WHERE origin=%s ORDER BY ts DESC LIMIT 1"
    sql_last_dt = f"SELECT {schema}.get_last_dt(%s)"

    sql_next = f"UPDATE {schema}.origin_schedule SET next_dt=NOW()+INTERVAL '%s SECOND' WHERE id=%s"

    sql_seconds = f"""
SELECT EXTRACT(EPOCH FROM s.next_dt - NOW())::INT AS seconds_until_next
FROM {schema}.origin o
LEFT JOIN {schema}.origin_schedule s using(id)
LEFT JOIN {schema}.origin_type t using(origin_type_id)
WHERE
t.protocol = '{ORIGIN_PROTOCOL}'
AND t.vendor = '{ORIGIN_VENDOR}'
AND o.is_enabled
AND s.is_enabled
AND CURRENT_TIME between start_time AND end_time
AND NOW() < next_dt
ORDER BY next_dt ASC
LIMIT 1
"""

    time_sleep = time_sleep_min
    while True:
        if time_sleep != 0:
            conn = psycopg2.connect(host=os.environ['POSTGRES_HOST'], port=os.environ.get('POSTGRES_PORT'), user=os.environ['POSTGRES_USER'], password=os.environ['POSTGRES_PASSWORD'], dbname=os.environ['POSTGRES_DB']        )
            cur = conn.cursor()

        point_ids = set()
        while True:
            cur.execute(sql_jobs)
            res = cur.fetchone()
            if not res:
#                logging.info(f"No jobs")
                break

            point_id, id, origin, credentials, poling_period_s, params = res
            point_ids.add(point_id)

            cur.execute(sql_last_dt, [origin])
            res = cur.fetchone()
            last_dt = res[0]
#            if res:
#                last_dt = res[0]
#            else:
#                last_dt = datetime(2025, 4, 26, 0, 0)

            try:
                count, end_time = run_job(credentials, origin, last_dt, params)
            except Exception as e:
                logging.exception("Error while running job")

            cur.execute(sql_next, [poling_period_s, id])
            conn.commit()

        cur.execute(sql_seconds)
        res = cur.fetchone()
        if res:
            time_sleep = res[0]
        else:
            time_sleep = time_sleep_max

        if time_sleep < time_sleep_min:
            time_sleep = time_sleep_min

        if time_sleep > time_sleep_max:
            time_sleep = time_sleep_max

#        logging.info(f"New time_sleep: {time_sleep}")
        if time_sleep == 0: continue

        cur.close()
        conn.close()

        for point_id in point_ids:
            if point_id:
                response = requests.post(OSD_URL, data={'point_id': point_id})

        logging.info(f"Sleep {time_sleep}s")
        time.sleep(time_sleep)
#        logging.info(f"Wake up")

if __name__ == "__main__":
#    load_dotenv()
    main()

