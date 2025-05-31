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
    return_code = camera.get_detection2(start_time, end_time)
    camera.close_factory()

    if return_code != 200:
        return 0, None

    cnt = 0
    for e in camera.items:
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

    logging.info(f"Parsed {cnt}. Last event {end_time}")
    return cnt, end_time

if __name__ == "__main__":
    import os
    from dotenv import dotenv_values

    credentials = dotenv_values('.env_dah')
    origin = 'sezon_DAH_1'
    origin_id = 21
    last_dt = datetime.now() + timedelta(seconds=-36000)

    params = None

    count, end_time = dah_runner(credentials, origin, origin_id, last_dt, params)
    print(count, end_time)
