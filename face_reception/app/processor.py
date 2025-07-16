#!/usr/bin/python3
import uuid
import json
from io import BytesIO
from PIL import Image, ImageFile

from db_wrapper import DB
from service_exchange import Service_exchange

from singleton import SingletonMeta

ImageFile.LOAD_TRUNCATED_IMAGES = True

def get_demography_from(title):
    try:
        src = json.loads(title)
    except Exception as e:
        return None
    if 'age' in src:
        if isinstance(src['age'], int):
            pass
        elif src['age'].isdigit():
            src['age'] = int(src['age'])
        else:
            src['age'] = None
    for k, v in {'sex': 'dominant_gender', 'nation': 'dominant_race', 'emotion': 'dominant_emotion'}.items():
        if k in src:
            src[v] = src[k]
            del src[k]
    return src

class Processor(metaclass=SingletonMeta):
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

    def __init__(self):
        self.se = Service_exchange()
        self.db = DB()
        self.lock = False

    def execute(self):
        if self.lock: return
        self.lock = True

        self.db.open()

        while True:
            self.db.cursor.execute(sql_target)
            res = self.db.cursor.fetchone()
            if not res: break

            file_uuid = res[0]
            engine_embedding = res[1].get('embedding') if res[1] else None
            engine_demography = res[1].get('demography') if res[1] else None
            engine_detection = res[1].get('face_detection') if res[1] else None
            face_width_px = res[1].get('face_width_px', 0) if res[1] else 0
            title = res[2]
            self.db.conn.commit()

            if not engine_embedding:
                continue

            demography = None
            if not engine_demography:
                demography = get_demography_from(title)

            content = self.se.get_img(file_uuid)
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

            data = self.se.post_engine(url, data, files)
            if not data:
                continue

            file_data.seek(0)
            image = Image.open(file_data)

            face_idx = 0
            for face_idx, row in enumerate(data, 1):
                if row['face_confidence'] == 0:
                    face_idx = 0
                    break
                face_uuid = uuid.uuid4().hex
                values = (face_uuid, file_uuid, face_idx, row['embedding'], json.dumps(row['facial_area']), row['face_confidence'], json.dumps(demography) if demography else None)
                self.db.cursor.execute(sql_insert, values)
                self.db.conn.commit()

                delta_x = 25 * row['facial_area']['w'] / 100
                delta_y = 25 * row['facial_area']['h'] / 100

                img = image.crop((row['facial_area']['x'] - delta_x, row['facial_area']['y'] - delta_y, row['facial_area']['x'] + row['facial_area']['w'] + delta_x, row['facial_area']['y'] + row['facial_area']['h'] + delta_y))
                buffer = BytesIO()
                img.save(buffer, format='JPEG')
                buffer.seek(0)

                content = self.se.set_img(face_uuid, buffer)
                if not content:
                    break

                self.se.launch_service('demography')

            self.db.cursor.execute(self.sql_update, (face_idx, file_uuid))
            self.db.conn.commit()

        self.db.close()

        self.lock = False

if __name__ == "__main__":
#    from dotenv import load_dotenv
#    load_dotenv()

    processor = Processor()
    processor.execute()
