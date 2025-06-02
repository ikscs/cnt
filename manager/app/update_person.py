#!/usr/local/bin/python
import os
import sys
import json
from io import BytesIO
import requests
import psycopg2

KV_DB_URL = 'http://kv_db:5000'

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


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print('person_id not given')
        exit(1)

    try:
        person_id = int(sys.argv[1])
    except Exception as err:
        print(f'Wrong person_id {argv[1]}')
        exit(1)

    db = DB()
    db.open()

    sql = f'''
SELECT face_uuid, photo, embedding
FROM face_referer_data
WHERE person_id={person_id};'''

    db.cursor.execute(sql)
    result = db.cursor.fetchall()

    if not result:
        print(f'No data for person_id: {person_id}')
        db.close()
        exit(0)

    sql_update = f'UPDATE face_referer_data SET embedding=%s WHERE face_uuid=%s;'

    sql = f'''
SELECT entry_point, backend, model, param->'embedding' AS e_param FROM method
LEFT JOIN point ON method_id=embedding_id
LEFT JOIN person_group USING(point_id)
LEFT JOIN person USING(group_id)
WHERE person_id={person_id};'''

    db.cursor.execute(sql)
    result1 = db.cursor.fetchone()
    if result1:
        entry_point = result1[0]
        backend = result1[1]
        model = result1[2]
        e_param = result1[3]
    if not entry_point:
        print(f'No embedding entry point for person_id: {person_id}')
        db.close()
        exit(0)

    data_out = e_param if e_param else {}
    data_out['fmt'] = 'json'
    data_out['backend'] = backend
    data_out['model'] = model

    url = f'{entry_point}/represent.json'

    output = []
    for face_uuid, photo, embedding in result:
        if photo == None:
            try:
                r = requests.get(f"{kv_db_url}/get/{face_uuid}")
                r.raise_for_status()
                content = r.content
            except Exception as err:
                content = None
        else:
            content = photo if photo else None

        if not content:
            output.append([None, face_uuid])
            continue

        file_data = BytesIO(content)
        files = {'f': (face_uuid, file_data, 'application/octet-stream')}

        try:
            response = requests.post(url, data=data_out, files=files)
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
            output.append([data[0].get('embedding'), face_uuid])
        else:
            output.append([None, face_uuid])

    if output:
        db.cursor.executemany(sql_update, output)
        db.conn.commit()

    res = sum(1 for e in output if e[0])
    print(f'Person_id {person_id} updated {res}/{len(output)}')

    db.close()
