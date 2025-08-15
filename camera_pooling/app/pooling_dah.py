from datetime import datetime, timedelta
from service_exchange import Service_exchange
import json
import logging

from camera_dah import Camera

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def get_dict_value(src, *keys):
    result = src
    for key in keys:
        result = result.get(key)
        if result == None:
            break
    return result

def dah_runner(credentials, origin, origin_id, last_dt, params):
    logging.info(f"Running periodic task for {origin} from {last_dt}")

    se = Service_exchange()

    camera = Camera(credentials, max_results=50)
    if not camera.is_connected:
        logging.error(camera.error_txt)
        return 0, None

    start_time = (last_dt + timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S")

    now = datetime.now()
    end_time = (now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")

    camera.open_factory()
    if params['event'] == 'FaceDetection':
        return_code = camera.get_detection2(start_time, end_time)
    elif params['event'] == 'CrossLineDetection':
        return_code = camera.get_crossline(start_time, end_time)
    else:
        return 0, None
    camera.close_factory()

    if return_code != 200:
        return 0, None

    cnt = 0
    cross_events = []
    for e in camera.items:
        if params['event'] == 'FaceDetection':
            image_name = get_dict_value(e, 'summary', 'file_path')

            title = dict()
            for param in ('sex', 'age', 'glasses', 'emotion', 'mask', 'beard', 'nation'):
                title[param] = get_dict_value(e, 'summary', param)
            for param in ('glasses', 'mask', 'beard'):
                title[param] = {'0': None, '1': False, '2': True}.get(title[param])

            if image_name:
                #end_event = get_dict_value(e, 'event_time')
                end_time = get_dict_value(e, 'end_time')
                content = camera.get_media(image_name)
                image_name = image_name.split('=')[-1]
                se.checkin(origin, origin_id, json.dumps(title), image_name, content, end_time)
                cnt += 1
            else:
                return 0, None

        elif params['event'] == 'CrossLineDetection':
            end_time = get_dict_value(e, 'end_time')
            file_name = e['file_path']
            content = camera.get_media(file_name)
            cross_events.append({'origin': origin, 'origin_id': origin_id, 'ts': end_time, 'prefix': e['events'], 'name': file_name})
            se.checkin(origin, origin_id, e['events'], file_name, content, end_time)
            cnt += 1

    if cross_events:
        se.upload_events(cross_events)

    logging.info(f"Parsed {cnt}. Last event {end_time}")
    return cnt, end_time

if __name__ == "__main__":
    import os
    from dotenv import dotenv_values

#    credentials = dotenv_values('.env_dah')
    credentials = dotenv_values('.env_dah_camera')
    origin = 'office_hik_camera'
    origin_id = 45
    last_dt = datetime.now() + timedelta(seconds=-3600)

#    params = {'event': 'FaceDetection'}
    params = {'event': 'CrossLineDetection'}

    count, end_time = dah_runner(credentials, origin, origin_id, last_dt, params)
    print(count, end_time)
