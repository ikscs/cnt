import os
import sys
import uuid
import psycopg2
import requests
import subprocess

from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional

class Event_record(BaseModel):
    origin: str
    ts: str
    prefix: str
    name: str

#from dotenv import load_dotenv
#load_dotenv()

KV_DB_URL = 'http://kv_db:5000'
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
PROCESSOR_SCRIPT = DIR_PATH + "/processor.py"

class PgDb():
    event_keys = ['origin', 'ts', 'prefix', 'name']

    def __init__(self):
        self.schema = os.environ['POSTGRES_SCHEMA']
        self.conn = psycopg2.connect(
            host=os.environ['POSTGRES_HOST'],
            port=os.environ.get('POSTGRES_PORT'),
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'],
            dbname=os.environ['POSTGRES_DB']
        )
        self.cursor = self.conn.cursor()

        self.sql_insert_incoming_with_ts = f"INSERT INTO {self.schema}.incoming (file_uuid, origin, origin_id, title, filename, ts) VALUES(%s, %s, {self.schema}.get_id_by_origin(%s), %s, %s, %s) ON CONFLICT (file_uuid) DO NOTHING"
        self.sql_insert_incoming_without_ts = f"INSERT INTO {self.schema}.incoming (file_uuid, origin, origin_id, title, filename) VALUES(%s, %s, {self.schema}.get_id_by_origin(%s), %s, %s) ON CONFLICT (file_uuid) DO NOTHING"

        fields = ', '.join(self.event_keys)
        vars_cnt = ','.join(['%s']*len(self.event_keys))
        self.sql_insert_event = f"INSERT INTO {self.schema}.event_crossline ({fields}) VALUES({vars_cnt}) ON CONFLICT ({fields}) DO NOTHING"

    def close(self):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def hello():
    body = '''<form action="upload.json" method="POST" enctype="multipart/form-data">
<label for="origin">origin (From):</label><input type="text" id="origin" name="origin"><br>
<label for="title">title (Subject):</label><input type="text" id="title" name="title"><br>
<input type='file' name='f'><br>
<input type='submit' value='submit'>
</form>
'''
    data = '<html><head></head>'
    data += '<link rel="icon" href="data:image/png;base64,iVBORw0KGgo=">'
    data += '<body>'
    data += body
    data += '</body></html>'

    return data

@app.post('/upload.json', response_class=HTMLResponse)
async def upload_json(
    origin: str = Form(...),
    title: str = Form(...),
    f: UploadFile = File(...),
    ts: str = Form(None)
):

    file_uuid = uuid.uuid4().hex
    contents = await f.read()

    headers = {"Content-Type": "application/octet-stream"}
    response = requests.post(f"{KV_DB_URL}/set/{file_uuid}", headers=headers, data=contents)
#    print(response.text)

    db = PgDb()

    if ts:
        sql = db.sql_insert_incoming_with_ts
        data = [file_uuid, origin, origin, title, f.filename, ts]
    else:
        sql = db.sql_insert_incoming_without_ts
        data = [file_uuid, origin, origin, title, f.filename]

    db.cursor.execute(sql, data)
    db.close()

    try:
        process = subprocess.Popen([sys.executable, PROCESSOR_SCRIPT],
            #stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except Exception as e:
        print(str(e))

    return file_uuid

@app.post('/events.json')
async def upload_json(
    events: List[Event_record]
):

    db = PgDb()
    data = [[getattr(row, e, None) for e in db.event_keys] for row in events]
    db.cursor.executemany(db.sql_insert_event, data)
    db.close()

    return JSONResponse(content={'result': 'Ok', 'count': len(data)})
