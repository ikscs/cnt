#!/usr/bin/python3
import os
import sys
import requests
import uuid
import json
from io import BytesIO
from PIL import Image, ImageFile
from run_once import run_once

ImageFile.LOAD_TRUNCATED_IMAGES = True

import subprocess
import psycopg2
#from dotenv import load_dotenv

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
DEMOGRAPHY_SCRIPT = DIR_PATH + "/demograph.py"

kv_db_url = 'http://kv_db:5000'

def main():
    conn = psycopg2.connect(
        host=os.environ['POSTGRES_HOST'],
        port=os.environ.get('POSTGRES_PORT'),
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD'],
        dbname=os.environ['POSTGRES_DB']
    )

    cur = conn.cursor()
    schema = os.environ['POSTGRES_SCHEMA']

    sql1 = f'''
WITH one_row AS (
SELECT file_uuid FROM {schema}.incoming
WHERE faces_cnt IS NULL ORDER BY ts ASC LIMIT 1
)
UPDATE {schema}.incoming SET faces_cnt=-1
WHERE file_uuid IN (SELECT file_uuid FROM one_row)
RETURNING file_uuid, {schema}.get_engine(file_uuid) AS engine;
'''

    while True:
        cur.execute(sql1)
        res = cur.fetchone()
        if not res: break
        file_uuid = res[0]
        engine = res[1].get('embedding') if res[1] else None
        face_width_px = res[1].get('face_width_px', 0) if res[1] else 0
        conn.commit()
        if not engine:
            continue

        try:
            r = requests.get(f"{kv_db_url}/get/{file_uuid}")
            r.raise_for_status()
        except Exception as err:
            print('Download img: ', err)
            continue

        file_data = BytesIO(r.content)
        files = {'f': (file_uuid, file_data, 'application/octet-stream')}

        data = engine['param'] if engine['param'] else {}
        if data.get('area'):
            data['area'] = max((data['area'], face_width_px))
        else:
            data['area'] = face_width_px

        data['fmt'] = 'json'
        data['backend'] = engine['backend']
        data['model'] = engine['model']
        url = f"{engine['entry_point']}/represent.json"

        try:
            response = requests.post(url, data=data, files=files)
        except Exception as err:
            print('Engine error: ', err)
            break

        if response.status_code != 200:
            print(f'{url} status_code: ', response.status_code)
            break

        try:
            data = response.json()
        except Exception as err:
            print(err)
            break

        if data:
            file_data.seek(0)
            image = Image.open(file_data)

        sql = f"INSERT INTO {schema}.face_data (face_uuid, file_uuid, face_idx, embedding, facial_area, confidence) VALUES(%s, %s, %s, %s, %s, %s) ON CONFLICT (face_uuid) DO NOTHING"
        face_idx = 0
        for face_idx, row in enumerate(data, 1):
            if row['face_confidence'] == 0:
                face_idx = 0
                break
            face_uuid = uuid.uuid4().hex
            values = (face_uuid, file_uuid, face_idx, row['embedding'], json.dumps(row['facial_area']), row['face_confidence'])
            cur.execute(sql, values)
            conn.commit()

            delta_x = 25 * row['facial_area']['w'] / 100
            delta_y = 25 * row['facial_area']['h'] / 100

            img = image.crop((row['facial_area']['x'] - delta_x, row['facial_area']['y'] - delta_y, row['facial_area']['x'] + row['facial_area']['w'] + delta_x, row['facial_area']['y'] + row['facial_area']['h'] + delta_y))
            buffer = BytesIO()
            img.save(buffer, format='JPEG')
            buffer.seek(0)

            headers = {"Content-Type": "application/octet-stream"}

            try:
                response = requests.post(f"{kv_db_url}/set/{face_uuid}", headers=headers, data=buffer)
            except Exception as err:
                print('Upload img: ', err)
                break

            try:
                process = subprocess.Popen([sys.executable, DEMOGRAPHY_SCRIPT],
                    #stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            except Exception as e:
                print(str(e))

        sql = f"UPDATE {schema}.incoming SET faces_cnt={face_idx} WHERE file_uuid = '{file_uuid}'"
        cur.execute(sql)
        conn.commit()

    cur.close()
    conn.close()

if __name__ == "__main__":
#    load_dotenv()
    run_once(main)
