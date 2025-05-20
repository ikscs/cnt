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

deep_face_url = 'http://deep_face:8000/demography.json'

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
WITH one_row AS (SELECT face_uuid FROM {schema}.face_data WHERE demography IS NULL ORDER BY ts ASC LIMIT 1)
UPDATE {schema}.face_data SET demography='{{}}' WHERE face_uuid IN (SELECT face_uuid FROM one_row)
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
        data = {'backend': 'retinaface', 'actions': 'age, gender, race, emotion'}
        files = {'f': (face_uuid, face_data, 'application/octet-stream')}

        try:
            response = requests.post(deep_face_url, data=data, files=files)
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
            #Get ref_id, ts, time_period name
            sql = f'''
SELECT i.ts, o.ref_id, p.time_period FROM {schema}.face_data d
LEFT JOIN {schema}.incoming i using(file_uuid)
LEFT JOIN {schema}.origin o using(origin)
LEFT JOIN {schema}.point p using(point_id)
WHERE d.face_uuid = %s;
'''
            cur.execute(sql, [face_uuid])
            res = cur.fetchone()
            if not res: continue
            ts = res[0]
            ref_id = res[1]
            time_period = res[2]

            sql = f'''
UPDATE {schema}.face_data
SET demography=%s, hash={schema}.make_hash(%s, embedding), time_slot={schema}.get_time_slot(%s, %s)
WHERE face_uuid = %s;
'''
            cur.execute(sql, [json.dumps(data[0]), ref_id, time_period, ts, face_uuid])
            conn.commit()

            try:
                process = subprocess.Popen(
                    [sys.executable, SIMILARITY_SCRIPT, '1', 'hash', 'neighbors', 'euclidean', 'demography'],
                    #stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            except Exception as e:
                print(str(e))

            try:
                process = subprocess.Popen(
                    [sys.executable, SIMILARITY_SCRIPT, '3', 'embedding', 'neighbors3', 'cosine', 'demography'],
                    #stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            except Exception as e:
                print(str(e))

            try:
                process = subprocess.Popen(
                    [sys.executable, SIMILARITY_SCRIPT, '4', 'embedding', 'neighbors4', 'euclidean', 'demography'],
                    #stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            except Exception as e:
                print(str(e))

    cur.close()
    conn.close()

if __name__ == "__main__":
#    load_dotenv()
    run_once(main)
