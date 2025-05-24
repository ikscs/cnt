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

kv_db_url = 'http://kv_db:5000'

class DB:
    def open(self):
        self.conn = psycopg2.connect(host=os.environ['POSTGRES_HOST'], port=os.environ.get('POSTGRES_PORT'),
            user=os.environ['POSTGRES_USER'], password=os.environ['POSTGRES_PASSWORD'],
            dbname=os.environ['POSTGRES_DB']
        )
        self.cursor = self.conn.cursor()
        self.schema = os.environ['POSTGRES_SCHEMA']
        sql = f'SET search_path = {self.schema}, "$user", public;'
        self.cursor.execute(sql)

    def close(self):
        self.cursor.close()
        self.conn.close()

def main():
    db = DB()
    db.open()

    sql1 = f'''
WITH one_row AS (
SELECT face_uuid, i.ts, p.time_period FROM face_data d
LEFT JOIN incoming i using(file_uuid)
LEFT JOIN origin o using(origin)
LEFT JOIN point p using(point_id)
WHERE demography IS NULL ORDER BY ts ASC LIMIT 1
)
UPDATE face_data d SET demography='{{}}', time_slot=get_time_slot(r.time_period, r.ts)
FROM one_row AS r
WHERE r.face_uuid = d.face_uuid
RETURNING face_uuid, get_engine(file_uuid) AS engine;
'''

    while True:
        cur.execute(sql1)
        res = cur.fetchone()
        if not res: break
        face_uuid = res[0]
        engine = res[1].get('demography') if res[1] else None
        face_width_px = res[1].get('face_width_px', 0) if res[1] else 0
        db.conn.commit()
        if not engine:
            continue

        try:
            r = requests.get(f"{kv_db_url}/get/{face_uuid}")
            r.raise_for_status()
        except Exception as err:
            print(err)
            continue

        face_data = BytesIO(r.content)
        files = {'f': (face_uuid, face_data, 'application/octet-stream')}

        data = engine['param'] if engine['param'] else {}
        if data.get('area'):
            data['area'] = max((data['area'], face_width_px))
        else:
            data['area'] = face_width_px

        url = f"{engine['entry_point']}/demography.json"

        try:
            response = requests.post(url, data=data, files=files)
        except Exception as err:
            print(err)
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

            sql = f'UPDATE face_data SET demography=%s WHERE face_uuid = %s;'
            cur.execute(sql, [json.dumps(data[0]), face_uuid])
            db.conn.commit()

            try:
                process = subprocess.Popen([sys.executable, SIMILARITY_SCRIPT, '1', 'embedding', 'neighbors', 'cosine', 'demography'])
            except Exception as e:
                print(str(e))

    db.close()

if __name__ == "__main__":
#    load_dotenv()
    run_once(main)
