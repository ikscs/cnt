#!/usr/bin/python3
import uuid
import json
from io import BytesIO
from PIL import Image, ImageFile

from run_once import run_once
from db_wrapper import DB
from service_exchange import Service_exchange

ImageFile.LOAD_TRUNCATED_IMAGES = True

def main():
    se = Service_exchange()
    db = DB()
    db.open()

    sql_mk_time_slot = '''
WITH many_rows AS (
SELECT face_uuid, i.ts, p.time_period, demography FROM face_data d
LEFT JOIN incoming i using(file_uuid)
LEFT JOIN origin o using(origin)
LEFT JOIN point p using(point_id)
WHERE demography IS NOT NULL
AND time_slot IS NULL
ORDER BY ts ASC
)
UPDATE face_data d SET time_slot=get_time_slot(r.time_period, r.ts)
FROM many_rows AS r
WHERE r.face_uuid = d.face_uuid;
'''
    db.cursor.execute(sql_mk_time_slot)
    db.conn.commit()

    sql_target = '''
WITH one_row AS (
SELECT face_uuid, i.ts, p.time_period FROM face_data d
LEFT JOIN incoming i using(file_uuid)
LEFT JOIN origin o using(origin)
LEFT JOIN point p using(point_id)
WHERE demography IS NULL ORDER BY ts ASC LIMIT 1
)
UPDATE face_data d SET demography='{}', time_slot=get_time_slot(r.time_period, r.ts)
FROM one_row AS r
WHERE r.face_uuid = d.face_uuid
RETURNING r.face_uuid, get_engine(file_uuid) AS engine;
'''
    sql_update = 'UPDATE face_data SET demography=%s WHERE face_uuid = %s;'

    while True:
        db.cursor.execute(sql_target)
        res = db.cursor.fetchone()
        if not res: break
        face_uuid = res[0]
        engine = res[1].get('demography') if res[1] else None
        face_width_px = res[1].get('face_width_px', 0) if res[1] else 0
        db.conn.commit()
        if not engine:
            continue

        content = se.get_img(face_uuid)
        if not content:
            continue

        file_data = BytesIO(content)
        files = {'f': (face_uuid, file_data, 'application/octet-stream')}

        data = engine['param'] if engine['param'] else {}
        if data.get('area'):
            data['area'] = max((data['area'], face_width_px))
        else:
            data['area'] = face_width_px

        url = f"{engine['entry_point']}/demography.json"

        data = se.post_engine(url, data, files)
        if not data:
            break

        if data:

            db.cursor.execute(sql_update, [json.dumps(data[0]), face_uuid])
            db.conn.commit()

            se.launch('SIMILARITY')

    db.close()

if __name__ == "__main__":
#    from dotenv import load_dotenv
#    load_dotenv()
    run_once(main)
