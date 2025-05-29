#!/usr/bin/python3
import os
import sys
import uuid
import json
from io import BytesIO
from PIL import Image, ImageFile
import subprocess

from run_once import run_once
from db_wrapper import DB
from service_exchange import Service_exchange

ImageFile.LOAD_TRUNCATED_IMAGES = True

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
DEMOGRAPHY_SCRIPT = DIR_PATH + "/demograph.py"

def main():
    se = Service_exchange()
    db = DB()
    db.open()

    sql_target = '''
WITH one_row AS (
SELECT file_uuid FROM incoming
WHERE faces_cnt IS NULL
ORDER BY ts ASC LIMIT 1
)
UPDATE incoming SET faces_cnt=-1
WHERE file_uuid IN (SELECT file_uuid FROM one_row)
RETURNING file_uuid, get_engine(file_uuid) AS engine, title;
'''
    sql_insert = "INSERT INTO face_data (face_uuid, file_uuid, face_idx, embedding, facial_area, confidence, demography) VALUES(%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (face_uuid) DO NOTHING"
    sql_update = "UPDATE incoming SET faces_cnt=%s WHERE file_uuid=%s"

    while True:
        db.cursor.execute(sql_target)
        res = db.cursor.fetchone()
        if not res: break

        file_uuid = res[0]
        engine_embedding = res[1].get('embedding') if res[1] else None
        engine_demography = res[1].get('demography') if res[1] else None
        engine_detection = res[1].get('face_detection') if res[1] else None
        face_width_px = res[1].get('face_width_px', 0) if res[1] else 0
        title = res[2]
        db.conn.commit()

        if not engine_embedding:
            continue

        demography = None
        if not engine_demography:
            try:
                demography = json.loads(title)
            except Exception as e:
                pass

        content = get_img(file_uuid)
        if not content:
            continue

        file_data = BytesIO(content)
        files = {'f': (file_uuid, file_data, 'application/octet-stream')}

        data = engine_embedding['param'] if engine_embedding['param'] else {}
        if data.get('area'):
            data['area'] = max((data['area'], face_width_px))
        else:
            data['area'] = face_width_px

        data['fmt'] = 'json'
        data['backend'] = engine_embedding['backend']
        data['model'] = engine_embedding['model']
        url = f"{engine_embedding['entry_point']}/represent.json"

        data = se.post_engine(url, data, files)
        if not data:
            break

        file_data.seek(0)
        image = Image.open(file_data)

        face_idx = 0
        for face_idx, row in enumerate(data, 1):
            if row['face_confidence'] == 0:
                face_idx = 0
                break
            face_uuid = uuid.uuid4().hex
            values = (face_uuid, file_uuid, face_idx, row['embedding'], json.dumps(row['facial_area']), row['face_confidence'], demography)
            db.cursor.execute(sql_insert, values)
            db.conn.commit()

            delta_x = 25 * row['facial_area']['w'] / 100
            delta_y = 25 * row['facial_area']['h'] / 100

            img = image.crop((row['facial_area']['x'] - delta_x, row['facial_area']['y'] - delta_y, row['facial_area']['x'] + row['facial_area']['w'] + delta_x, row['facial_area']['y'] + row['facial_area']['h'] + delta_y))
            buffer = BytesIO()
            img.save(buffer, format='JPEG')
            buffer.seek(0)

            content = set_img(face_uuid, buffer)
            if not content:
                break

            try:
                process = subprocess.Popen([sys.executable, DEMOGRAPHY_SCRIPT],
                    #stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            except Exception as e:
                print(str(e))

        db.cursor.execute(sql_update, (face_idx, file_uuid))
        db.conn.commit()

    db.close()

if __name__ == "__main__":
#    from dotenv import load_dotenv
#    load_dotenv()
    run_once(main)
