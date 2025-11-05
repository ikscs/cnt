from datetime import datetime, timedelta
import logging

from camera_tyto import Camera

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def tyto_runner(credentials, entity_id, last_dt, params):
    logging.info(f"Running periodic task for {entity_id} from {last_dt}")

    camera = Camera(credentials)
    if not camera.is_connected:
        logging.error(camera.error_txt)
        return None, None

    start_time = last_dt + timedelta(seconds=1)

    results = camera.load_plate_events(start_time, datetime.now())

    end_time = results[-1][1] if results else None

    logging.info(f"Parsed {len(results)}. Last event {end_time}")

    return results, end_time

if __name__ == "__main__":
    import os
    from dotenv import dotenv_values

    credentials = dotenv_values('.env')

    entity_id = 5
    last_dt = datetime.now() + timedelta(seconds=-3600)

    params = None

    results, end_time = tyto_runner(credentials, entity_id, last_dt, params)

    if results:
        for result in results:
            print(result)

    print(end_time)
