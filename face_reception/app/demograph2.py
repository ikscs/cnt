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
SIMILARITY_SCRIPT = DIR_PATH + "/similarity.py"

face_recognition_url = 'http://face_recognition:8000'
face_recognition_represent_url = f'{face_recognition_url}/represent.json'
face_recognition_demography_url = f'{face_recognition_url}/demography.json'

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
WITH one_row AS (SELECT face_uuid FROM {schema}.face_data WHERE demography2 IS NULL ORDER BY ts ASC LIMIT 1)
UPDATE {schema}.face_data SET demography2='{{}}' WHERE face_uuid IN (SELECT face_uuid FROM one_row)
RETURNING face_uuid
'''
#RETURNING face_uuid, file_uuiid#...maybe

    while True:
        cur.execute(sql1)
        res = cur.fetchone()
        if not res: break
        face_uuid = res[0]
        conn.commit()

        try:
            r = requests.get(f"{kv_db_url}/get/{face_uuid}")
            r.raise_for_status()
        except Exception as err:
            print(err)
            continue

        face_data = BytesIO(r.content)
        data = {'fmt': 'json', 'confidence': 0.8, 'area': 40}
        files = {'f': (face_uuid, face_data, 'application/octet-stream')}

        try:
            response = requests.post(face_recognition_represent_url, data=data, files=files)
        except Exception as err:
            print(err)
            break

        if response.status_code != 200:
            print('status_code: ', response.status_code)
            break

        try:
            embedding = response.json()
        except Exception as err:
            print(err)
            break

        face_data.seek(0)
        data = {'actions': 'age, gender, race, emotion'}
#        files = {'f': (face_uuid, face_data, 'application/octet-stream')}

        try:
            response = requests.post(face_recognition_demography_url, data=data, files=files)
        except Exception as err:
            print(err)
            break

        if response.status_code != 200:
            print('status_code: ', response.status_code)
            break

        try:
            data = response.json()
        except Exception as err:
            print(err)
            break

        if data:
            #Get ts, time_period name
            sql = f'''
SELECT i.ts, p.time_period FROM {schema}.face_data d
LEFT JOIN {schema}.incoming i using(file_uuid)
LEFT JOIN {schema}.origin o using(origin)
LEFT JOIN {schema}.point p using(point_id)
WHERE d.face_uuid = %s;
'''
            cur.execute(sql, [face_uuid])
            res = cur.fetchone()
            if not res: continue
            ts = res[0]
            time_period = res[1]

            sql = f'''
UPDATE {schema}.face_data
SET embedding2=%s, demography2=%s, time_slot={schema}.get_time_slot(%s, %s)
WHERE face_uuid = %s;
'''
            cur.execute(sql, [embedding[0]['embedding'], json.dumps(data[0]), time_period, ts, face_uuid])
            conn.commit()

            try:
                process = subprocess.Popen(
                    [sys.executable, SIMILARITY_SCRIPT, '2', 'embedding2', 'neighbors2', 'cosine', 'demography2'],
                    #stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            except Exception as e:
                print(str(e))

    cur.close()
    conn.close()

if __name__ == "__main__":
#    load_dotenv()
    run_once(main)
